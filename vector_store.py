"""
Minimal vector store using TF-IDF + cosine similarity.
No external binary dependencies -- works on any Python 3.11+.
Persists to a JSON file.

How it works:
  1. Each document chunk is converted to a TF-IDF vector (bag-of-words weighted by rarity)
  2. When you query, your question is also converted to a TF-IDF vector
  3. We find the chunks most similar to your question using cosine similarity
"""

import json
import math
import os
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase alphanumeric tokens (words/numbers)."""
    return re.findall(r"[a-z0-9]+", text.lower())


class VectorStore:
    def __init__(self, path: str = "./vector_store.json"):
        self.path = path
        self.documents: list[dict] = []          # stored chunks: {id, text, metadata}
        self.idf: dict[str, float] = {}          # inverse document frequency per word
        self.tfidf_vectors: list[dict[str, float]] = []  # one TF-IDF vector per chunk
        self.vocab: list[str] = []               # sorted list of all known words

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Term Frequency: how often each word appears in this chunk (normalized 0-1)."""
        counts = Counter(tokens)
        total = len(tokens) if tokens else 1
        return {t: c / total for t, c in counts.items()}

    def _build_index(self):
        """Build TF-IDF index over all stored documents."""
        # Tokenize every document
        all_tokens = [_tokenize(d["text"]) for d in self.documents]
        n = len(self.documents)

        # IDF: words that appear in fewer documents get higher scores (more distinctive)
        df = Counter()  # document frequency: how many docs contain each word
        for tokens in all_tokens:
            for t in set(tokens):  # set() so each word counted once per doc
                df[t] += 1
        self.idf = {t: math.log(n / count) for t, count in df.items()}
        self.vocab = sorted(self.idf.keys())

        # Build a TF-IDF vector for each document chunk
        # TF-IDF = term_frequency * inverse_document_frequency
        self.tfidf_vectors = []
        for tokens in all_tokens:
            tf = self._compute_tf(tokens)
            vec = {t: tf.get(t, 0) * self.idf.get(t, 0) for t in tf}
            self.tfidf_vectors.append(vec)

    def add(self, ids: list[str], documents: list[str], metadatas: list[dict]):
        """Add document chunks to the store and rebuild the index."""
        for id_, doc, meta in zip(ids, documents, metadatas):
            self.documents.append({"id": id_, "text": doc, "metadata": meta})
        self._build_index()
        self._save()

    def query(self, query_text: str, n_results: int = 3) -> dict:
        """Find the n_results most similar chunks to the query using cosine similarity."""
        # Convert query to TF-IDF vector (same process as documents)
        tokens = _tokenize(query_text)
        tf = self._compute_tf(tokens)
        # Only include words that exist in our vocabulary
        q_vec = {t: tf.get(t, 0) * self.idf.get(t, 0) for t in tf if t in self.idf}

        # Score each document chunk against the query
        scores = []
        for i, doc_vec in enumerate(self.tfidf_vectors):
            # Cosine similarity = dot_product / (magnitude_A * magnitude_B)
            dot = sum(q_vec.get(t, 0) * doc_vec.get(t, 0) for t in q_vec)
            mag_q = math.sqrt(sum(v ** 2 for v in q_vec.values())) or 1
            mag_d = math.sqrt(sum(v ** 2 for v in doc_vec.values())) or 1
            sim = dot / (mag_q * mag_d)
            scores.append((sim, i))

        # Sort by similarity (highest first) and take top results
        scores.sort(reverse=True)
        top = scores[:n_results]

        # Return in the same format as ChromaDB for compatibility
        return {
            "documents": [[self.documents[i]["text"] for _, i in top]],
            "metadatas": [[self.documents[i]["metadata"] for _, i in top]],
            "distances": [[1 - sim for sim, _ in top]],  # distance = 1 - similarity
        }

    def _save(self):
        """Persist documents to a JSON file."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([d for d in self.documents], f)

    def load(self) -> bool:
        """Load documents from JSON file and rebuild the index. Returns False if file missing."""
        if not os.path.exists(self.path):
            return False
        with open(self.path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        self._build_index()
        return True
