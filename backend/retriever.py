"""
Retriever — FAISS semantic search for similar past cases
Uses InLegalBERT embeddings for semantic similarity
"""

import pickle
import numpy as np
import faiss
import re
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer

MODELS_DIR      = "models"
EMBEDDING_MODEL = "law-ai/InLegalBERT"
SNIPPET_LEN     = 400


class Retriever:
    def __init__(self):
        print("  Loading FAISS index...")
        self.index = faiss.read_index(f"{MODELS_DIR}/faiss_index.bin")

        print("  Loading case store...")
        with open(f"{MODELS_DIR}/case_store.pkl", "rb") as f:
            self.case_store = pickle.load(f)

        print(f"  Loading embedding model: {EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

        print("  Retriever ready.")

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def get_similar_cases(self, query_text: str, top_k: int = 5):
        """
        Returns list of top_k similar past cases with:
        - text_snippet : first 400 chars of the case
        - label        : ACCEPTED or REJECTED
        - similarity   : cosine similarity score (0-1)
        """
        clean = self.clean_text(query_text)[:1500]

        # Embed query
        query_vec = self.embedder.encode(
            [clean],
            convert_to_numpy=True,
            show_progress_bar=False
        )
        query_vec = normalize(query_vec, norm="l2").astype(np.float32)

        # Search FAISS — returns top_k+1 to skip the query itself if present
        scores, indices = self.index.search(query_vec, top_k + 1)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.case_store):
                continue
            row   = self.case_store.iloc[idx]
            label = "ACCEPTED" if int(row["label"]) == 1 else "REJECTED"
            snippet = str(row["text"])[:SNIPPET_LEN].strip()

            results.append({
                "text_snippet": snippet,
                "label"       : label,
                "similarity"  : round(float(score), 4)
            })

            if len(results) >= top_k:
                break

        return results
