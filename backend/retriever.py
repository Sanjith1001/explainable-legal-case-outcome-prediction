"""
Retriever — hybrid legal case retrieval.

Combines:
- Dense semantic retrieval with InLegalBERT + FAISS
- Lexical retrieval over stored clean text
- Optional Indian Kanoon API enrichment hooks
"""

from __future__ import annotations

import json
import os
import pickle
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize

MODELS_DIR = "models"
EMBEDDING_MODEL = "law-ai/InLegalBERT"
SNIPPET_LEN = 400
MAX_QUERY_LEN = 1500

# Weighted blend of semantic similarity and lexical overlap.
SEMANTIC_WEIGHT = 0.72
LEXICAL_WEIGHT = 0.28


class Retriever:
    def __init__(self):
        print("  Loading FAISS index...")
        self.index = faiss.read_index(f"{MODELS_DIR}/faiss_index.bin")

        print("  Loading case store...")
        with open(f"{MODELS_DIR}/case_store.pkl", "rb") as f:
            self.case_store = pickle.load(f).reset_index(drop=True)

        print("  Loading lexical retrieval matrix...")
        clean_texts = self.case_store.get("clean_text")
        if clean_texts is None:
            clean_texts = self.case_store["text"].astype(str).tolist()
        else:
            clean_texts = clean_texts.fillna("").astype(str).tolist()

        self.lexical_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9,
            sublinear_tf=True,
        )
        self.lexical_matrix = self.lexical_vectorizer.fit_transform(clean_texts)

        print(f"  Loading embedding model: {EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

        self.indiankanoon_api_key = os.getenv("INDIANKANOON_API_KEY", "").strip()
        self.indiankanoon_enabled = os.getenv("INDIANKANOON_ENABLED", "0").strip() == "1"
        self.indiankanoon_endpoint = os.getenv(
            "INDIANKANOON_API_ENDPOINT",
            "https://api.indiankanoon.org/search/",
        ).strip()

        print("  Retriever ready.")

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _detect_match_reasons(self, query: str, case_text: str) -> list[str]:
        query_terms = [
            token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", query.lower())
            if len(token) >= 5
        ]
        case_lower = case_text.lower()

        matched_terms = []
        for term in query_terms:
            if term in case_lower and term not in matched_terms:
                matched_terms.append(term)
            if len(matched_terms) >= 3:
                break

        reasons = []
        if matched_terms:
            reasons.append(f"Shared legal terms: {', '.join(matched_terms)}")

        if any(term in case_lower for term in ("article 14", "article 19", "article 21")) and \
           any(term in query.lower() for term in ("article 14", "article 19", "article 21")):
            reasons.append("Constitutional issues overlap")

        if any(term in case_lower for term in ("appeal", "petition", "high court", "supreme court")) and \
           any(term in query.lower() for term in ("appeal", "petition", "high court", "supreme court")):
            reasons.append("Procedural posture is similar")

        return reasons[:3]

    def _hybrid_rank(self, clean_query: str, top_k: int) -> list[dict[str, Any]]:
        query_vec = self.embedder.encode(
            [clean_query],
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        query_vec = normalize(query_vec, norm="l2").astype(np.float32)

        semantic_scores, semantic_indices = self.index.search(query_vec, max(top_k * 3, 12))

        lexical_query = self.lexical_vectorizer.transform([clean_query])
        lexical_scores = linear_kernel(lexical_query, self.lexical_matrix).ravel()

        candidates: dict[int, dict[str, Any]] = {}
        for score, idx in zip(semantic_scores[0], semantic_indices[0]):
            if idx < 0 or idx >= len(self.case_store):
                continue
            candidates[idx] = {
                "semantic_score": float(score),
                "lexical_score": float(lexical_scores[idx]) if idx < len(lexical_scores) else 0.0,
            }

        if len(candidates) < top_k:
            extra_indices = np.argsort(lexical_scores)[::-1][: max(top_k * 2, 10)]
            for idx in extra_indices:
                idx = int(idx)
                if idx < 0 or idx >= len(self.case_store):
                    continue
                candidates.setdefault(
                    idx,
                    {
                        "semantic_score": 0.0,
                        "lexical_score": float(lexical_scores[idx]),
                    },
                )

        results = []
        for idx, scores in candidates.items():
            row = self.case_store.iloc[idx]
            label = "ACCEPTED" if int(row["label"]) == 1 else "REJECTED"
            snippet = str(row["text"])[:SNIPPET_LEN].strip()

            semantic = max(scores["semantic_score"], 0.0)
            lexical = max(scores["lexical_score"], 0.0)
            hybrid = (SEMANTIC_WEIGHT * semantic) + (LEXICAL_WEIGHT * lexical)

            results.append({
                "text_snippet": snippet,
                "label": label,
                "similarity": round(float(hybrid), 4),
                "semantic_score": round(float(semantic), 4),
                "lexical_score": round(float(lexical), 4),
                "source": "local_corpus",
                "source_name": "ILDC / project dataset",
                "match_reasons": self._detect_match_reasons(clean_query, str(row["text"])),
            })

        results.sort(
            key=lambda item: (
                item["similarity"],
                item["semantic_score"],
                item["lexical_score"],
            ),
            reverse=True,
        )
        return results[:top_k]

    def _search_indiankanoon(self, clean_query: str, top_k: int) -> list[dict[str, Any]]:
        if not (self.indiankanoon_enabled and self.indiankanoon_api_key):
            return []

        params = urllib.parse.urlencode({
            "formInput": clean_query[:300],
            "pagenum": 0,
        })
        url = f"{self.indiankanoon_endpoint}?{params}"
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Token {self.indiankanoon_api_key}",
                "Accept": "application/json",
                "User-Agent": "case-outcome-predictor/1.0",
            },
        )

        try:
            context = ssl.create_default_context()
            with urllib.request.urlopen(request, timeout=12, context=context) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError):
            return []

        docs = payload.get("docs", []) if isinstance(payload, dict) else []
        results = []
        for doc in docs[:top_k]:
            snippet = str(doc.get("headline") or doc.get("title") or doc.get("docsource") or "").strip()
            if not snippet:
                snippet = str(doc.get("docfragment") or "")[:SNIPPET_LEN].strip()
            results.append({
                "text_snippet": snippet[:SNIPPET_LEN],
                "label": "UNKNOWN",
                "similarity": round(0.45, 4),
                "semantic_score": 0.0,
                "lexical_score": 0.0,
                "source": "indiankanoon",
                "source_name": "Indian Kanoon API",
                "match_reasons": ["Retrieved from Indian Kanoon search"],
                "document_url": doc.get("tid") or doc.get("url") or "",
            })
        return results

    def get_similar_cases(self, query_text: str, top_k: int = 5):
        """
        Returns top_k similar past cases with a hybrid score and retrieval metadata.
        """
        clean = self.clean_text(query_text)[:MAX_QUERY_LEN]
        local_results = self._hybrid_rank(clean, top_k=top_k)

        # Optional enrichment path for future production/demo use.
        indiankanoon_results = self._search_indiankanoon(clean, top_k=2)

        return local_results + indiankanoon_results
