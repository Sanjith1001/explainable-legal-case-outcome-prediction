"""
Predictor — Loads TF-IDF + XGBoost and runs prediction
Uses calibrated threshold to fix class imbalance bias.
"""

import pickle
import numpy as np
import re

MODELS_DIR       = "models"
ACCEPT_THRESHOLD = 0.38   # lower than 0.5 to counter 62% rejected bias

class Predictor:
    def __init__(self):
        print("  Loading TF-IDF vectorizer...")
        with open(f"{MODELS_DIR}/tfidf_vectorizer.pkl", "rb") as f:
            self.tfidf = pickle.load(f)

        print("  Loading XGBoost model...")
        with open(f"{MODELS_DIR}/xgboost_model.pkl", "rb") as f:
            self.model = pickle.load(f)

        print(f"  Accept threshold: {ACCEPT_THRESHOLD}")
        print("  Predictor ready.")

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\.\,\;\:\(\)\-\/]", "", text)
        return text.strip()

    def predict_with_proba(self, text: str):
        clean = self.clean_text(text)
        vec   = self.tfidf.transform([clean])
        proba = self.model.predict_proba(vec)[0]

        prob_accepted = float(proba[1])
        prob_rejected = float(proba[0])

        if prob_accepted >= ACCEPT_THRESHOLD:
            label      = 1
            confidence = prob_accepted
        else:
            label      = 0
            confidence = prob_rejected

        # Cap at 92% — 100% confidence is unrealistic in legal domain
        confidence = min(confidence, 0.92)
        return label, confidence, proba

    def predict(self, text: str):
        label, confidence, _ = self.predict_with_proba(text)
        return label, confidence
