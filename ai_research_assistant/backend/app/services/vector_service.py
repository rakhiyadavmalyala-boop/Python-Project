import os
import math
import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class VectorService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.st_model = None
        self.chunks_db: List[Dict[str, Any]] = []  # In-memory index store
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        
        self._init_embedding_model()

    def _init_embedding_model(self):
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.st_model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"Warning: Could not load SentenceTransformer ({e}). Falling back to TF-IDF vector embeddings.")
                self.st_model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generates dense vector embeddings for input texts.
        """
        if not texts:
            return np.array([])
            
        if self.st_model is not None:
            return self.st_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        else:
            # Fallback: TF-IDF vectorizer mapping to dense array
            vectorizer = TfidfVectorizer(max_features=384)
            matrix = vectorizer.fit_transform(texts).toarray()
            # Normalize vectors to unit length
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return matrix / norms

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Adds new document chunks into the index and updates embedding and BM25 matrices.
        """
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        embeddings = self.encode(texts)

        for chunk, emb in zip(chunks, embeddings):
            chunk_copy = dict(chunk)
            chunk_copy["embedding"] = emb
            self.chunks_db.append(chunk_copy)

        self._rebuild_indices()

    def remove_document_chunks(self, document_id: str):
        """
        Purges chunks for a given document_id.
        """
        self.chunks_db = [c for c in self.chunks_db if c["document_id"] != document_id]
        self._rebuild_indices()

    def _rebuild_indices(self):
        """
        Rebuilds global dense matrix and TF-IDF matrix for keyword search.
        """
        if not self.chunks_db:
            self.embeddings_matrix = None
            self.tfidf_matrix = None
            self.tfidf_vectorizer = None
            return

        # Stack dense embeddings
        embeddings_list = [c["embedding"] for c in self.chunks_db]
        self.embeddings_matrix = np.vstack(embeddings_list)

        # Build TF-IDF for keyword matching
        all_texts = [c["text"] for c in self.chunks_db]
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)

    def search_semantic(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search using cosine similarity.
        """
        if not self.chunks_db or self.embeddings_matrix is None:
            return []

        query_embedding = self.encode([query])[0].reshape(1, -1)
        sim_scores = cosine_similarity(query_embedding, self.embeddings_matrix)[0]

        filtered_results = []
        for idx, score in enumerate(sim_scores):
            chunk = self.chunks_db[idx]
            if document_ids and chunk["document_id"] not in document_ids:
                continue
            res = dict(chunk)
            res.pop("embedding", None)
            res["score"] = float(score)
            res["search_mode"] = "semantic"
            filtered_results.append(res)

        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_k]

    def search_keyword(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs keyword BM25/TF-IDF match search.
        """
        if not self.chunks_db or self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            return []

        try:
            query_vec = self.tfidf_vectorizer.transform([query])
            scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        except Exception:
            scores = np.zeros(len(self.chunks_db))

        filtered_results = []
        for idx, score in enumerate(scores):
            chunk = self.chunks_db[idx]
            if document_ids and chunk["document_id"] not in document_ids:
                continue
            res = dict(chunk)
            res.pop("embedding", None)
            res["score"] = float(score)
            res["search_mode"] = "keyword"
            filtered_results.append(res)

        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_k]

    def search_hybrid(self, query: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search using Reciprocal Rank Fusion (RRF) between semantic and keyword search.
        """
        semantic_res = self.search_semantic(query, document_ids, top_k=top_k * 2)
        keyword_res = self.search_keyword(query, document_ids, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}
        k = 60  # RRF constant

        for rank, item in enumerate(semantic_res):
            cid = item["id"]
            chunk_map[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank + 1))

        for rank, item in enumerate(keyword_res):
            cid = item["id"]
            chunk_map[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank + 1))

        hybrid_results = []
        for cid, score in rrf_scores.items():
            res = dict(chunk_map[cid])
            res["score"] = float(round(score * 100, 4))  # Normalized RRF score
            res["search_mode"] = "hybrid"
            hybrid_results.append(res)

        hybrid_results.sort(key=lambda x: x["score"], reverse=True)
        return hybrid_results[:top_k]

# Global singleton vector service
vector_service = VectorService()
