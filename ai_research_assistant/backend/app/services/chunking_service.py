import uuid
from typing import List, Dict, Any
from app.core.config import settings

class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk_document_pages(self, document_id: str, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes page-level text dictionary and produces structured chunks with precise metadata.
        """
        all_chunks = []
        global_chunk_idx = 0

        for page_data in pages:
            page_number = page_data["page_number"]
            page_text = page_data["text"]

            if not page_text.strip():
                continue

            page_chunks = self._recursive_split(page_text, self.chunk_size, self.chunk_overlap)
            
            char_cursor = 0
            for chunk_text in page_chunks:
                start_char = page_text.find(chunk_text[:30], char_cursor)
                if start_char == -1:
                    start_char = char_cursor
                end_char = start_char + len(chunk_text)
                char_cursor = max(char_cursor, end_char - self.chunk_overlap)

                all_chunks.append({
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "page_number": page_number,
                    "chunk_index": global_chunk_idx,
                    "text": chunk_text,
                    "start_char": start_char,
                    "end_char": end_char
                })
                global_chunk_idx += 1

        return all_chunks

    def _recursive_split(self, text: str, max_size: int, overlap: int) -> List[str]:
        """
        Recursive character splitting algorithm trying highest semantic boundaries first.
        """
        text = text.strip()
        if len(text) <= max_size:
            return [text] if text else []

        # Find best separator
        separator = ""
        for sep in self.separators:
            if sep in text:
                separator = sep
                break

        splits = text.split(separator) if separator else list(text)
        
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            item = split + separator if separator else split
            item_len = len(item)

            if current_length + item_len > max_size:
                if current_chunk:
                    joined = "".join(current_chunk).strip()
                    if joined:
                        chunks.append(joined)
                
                # Overlap logic
                overlap_items = []
                overlap_len = 0
                for prev in reversed(current_chunk):
                    if overlap_len + len(prev) <= overlap:
                        overlap_items.insert(0, prev)
                        overlap_len += len(prev)
                    else:
                        break
                
                current_chunk = overlap_items + [item]
                current_length = overlap_len + item_len
            else:
                current_chunk.append(item)
                current_length += item_len

        if current_chunk:
            joined = "".join(current_chunk).strip()
            if joined:
                chunks.append(joined)

        return chunks
