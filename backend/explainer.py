"""
Explainer — SHAP-based explainability
Correctly maps SHAP values to legal interpretation.
"""

import numpy as np
import shap
import re


class Explainer:
    def __init__(self, vectorizer, model):
        self.vectorizer    = vectorizer
        self.model         = model
        self.feature_names = np.array(vectorizer.get_feature_names_out())

        print("  Initializing SHAP explainer...")
        self.explainer = shap.TreeExplainer(model)
        print("  Explainer ready.")

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def explain(self, text: str, top_n: int = 10):
        """
        Returns top_n SHAP keywords.
        Positive SHAP → pushes toward ACCEPTED
        Negative SHAP → pushes toward REJECTED
        """
        clean   = self.clean_text(text)
        vec     = self.vectorizer.transform([clean])
        vec_arr = vec.toarray()

        shap_values = self.explainer.shap_values(vec_arr)

        # XGBoost binary: shap_values is array of shape (1, n_features)
        # Positive = pushes toward class 1 (ACCEPTED)
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        # Only consider features present in this document
        present_mask  = vec_arr[0] > 0
        present_idx   = np.where(present_mask)[0]

        if len(present_idx) == 0:
            return []

        present_sv    = sv[present_idx]
        present_words = self.feature_names[present_idx]

        # Sort by absolute SHAP value descending
        sorted_order  = np.argsort(np.abs(present_sv))[::-1]

        results = []
        seen    = set()

        for i in sorted_order:
            word  = present_words[i]
            value = float(present_sv[i])

            if abs(value) < 1e-5:
                continue
            if word in seen:
                continue

            seen.add(word)
            results.append({
                "word"       : word,
                "shap_value" : round(value, 4),
                "direction"  : "supports_accepted" if value > 0 else "supports_rejected",
            })

            if len(results) >= top_n:
                break

        return results
