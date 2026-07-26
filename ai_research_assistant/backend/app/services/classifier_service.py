import os
import json
import numpy as np
from typing import Dict, Any, Tuple
from app.core.config import settings

class ClassifierService:
    def __init__(self):
        self.categories = [
            "Artificial Intelligence",
            "Machine Learning",
            "Computer Vision",
            "Natural Language Processing",
            "Robotics",
            "Cyber Security",
            "Cloud Computing"
        ]
        self.tf_model = None
        self.sklearn_vec = None
        self.sklearn_clf = None
        self._load_model()

    def _load_model(self):
        labels_path = settings.MODELS_DIR / "labels.json"
        if labels_path.exists():
            try:
                with open(labels_path, "r") as f:
                    data = json.load(f)
                    self.categories = data.get("categories", self.categories)
            except Exception as e:
                print(f"Notice loading labels: {e}")

        # 1. Try loading Keras / TensorFlow model
        keras_path = settings.MODELS_DIR / "tf_doc_classifier.keras"
        if keras_path.exists():
            try:
                import tensorflow as tf
                self.tf_model = tf.keras.models.load_model(str(keras_path))
                print("TensorFlow Document Classifier loaded successfully.")
                return
            except Exception as e:
                print(f"Could not load TensorFlow Keras model: {e}")

        # 2. Try loading Sklearn Joblib model
        vec_path = settings.MODELS_DIR / "tfidf_vec.joblib"
        clf_path = settings.MODELS_DIR / "mlp_clf.joblib"
        if vec_path.exists() and clf_path.exists():
            try:
                import joblib
                self.sklearn_vec = joblib.load(vec_path)
                self.sklearn_clf = joblib.load(clf_path)
                print("Sklearn fallback Document Classifier loaded successfully.")
                return
            except Exception as e:
                print(f"Could not load sklearn model: {e}")

        print("No persisted classification model found yet. Service will use keyword heuristic fallback until model is trained.")

    def classify_text(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classifies document text and returns (top_category, confidence, probability_dict).
        """
        if not text or not text.strip():
            return "Unclassified", 0.0, {cat: 0.0 for cat in self.categories}

        # 1. TensorFlow Inference
        if self.tf_model is not None:
            try:
                preds = self.tf_model.predict(np.array([text]), verbose=0)[0]
                top_idx = int(np.argmax(preds))
                category = self.categories[top_idx]
                confidence = float(preds[top_idx])
                prob_dict = {cat: float(preds[i]) for i, cat in enumerate(self.categories)}
                return category, confidence, prob_dict
            except Exception as e:
                print(f"TF Predict error ({e}), falling back...")

        # 2. Sklearn MLP Inference
        if self.sklearn_vec is not None and self.sklearn_clf is not None:
            try:
                X = self.sklearn_vec.transform([text]).toarray()
                probs = self.sklearn_clf.predict_proba(X)[0]
                top_idx = int(np.argmax(probs))
                category = self.categories[top_idx]
                confidence = float(probs[top_idx])
                prob_dict = {cat: float(probs[i]) for i, cat in enumerate(self.categories)}
                return category, confidence, prob_dict
            except Exception as e:
                print(f"Sklearn Predict error ({e}), falling back...")

        # 3. Domain Keyword Heuristic Classifier
        text_lower = text.lower()
        keyword_scores = {
            "Artificial Intelligence": text_lower.count("ai") * 2 + text_lower.count("intelligence") + text_lower.count("heuristic") + text_lower.count("symbolic"),
            "Machine Learning": text_lower.count("learning") * 2 + text_lower.count("regression") + text_lower.count("gradient") + text_lower.count("neural"),
            "Computer Vision": text_lower.count("vision") * 3 + text_lower.count("image") * 2 + text_lower.count("cnn") + text_lower.count("camera"),
            "Natural Language Processing": text_lower.count("nlp") * 3 + text_lower.count("transformer") * 2 + text_lower.count("text") + text_lower.count("bert"),
            "Robotics": text_lower.count("robot") * 3 + text_lower.count("kinematics") * 2 + text_lower.count("actuator") + text_lower.count("ros"),
            "Cyber Security": text_lower.count("security") * 3 + text_lower.count("crypto") * 2 + text_lower.count("threat") + text_lower.count("attack"),
            "Cloud Computing": text_lower.count("cloud") * 3 + text_lower.count("kubernetes") * 2 + text_lower.count("docker") + text_lower.count("microservice")
        }

        total_score = sum(keyword_scores.values())
        if total_score == 0:
            return "Machine Learning", 0.5, {cat: 1.0/len(self.categories) for cat in self.categories}

        prob_dict = {cat: round(score / total_score, 4) for cat, score in keyword_scores.items()}
        best_cat = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[best_cat]
        return best_cat, confidence, prob_dict

classifier_service = ClassifierService()
