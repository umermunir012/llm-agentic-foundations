"""
Ingest aviation safety documents into a TF-IDF vector store.

Pipeline: load .txt files -> chunk by character count -> index with TF-IDF.

Usage:
    python 02_rag_prototype/ingest.py [--data-dir 02_rag_prototype/data]

Configurable via environment variables (see .env.example):
    CHUNK_SIZE    - characters per chunk (default 512)
    CHUNK_OVERLAP - overlap in characters (default 64)
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from vector_store import VectorStore


def load_documents(data_dir: str) -> list[dict]:
    """Load all .txt files from a directory into memory."""
    docs = []
    for fname in sorted(os.listdir(data_dir)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(data_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        docs.append({"id": fname, "text": text, "source": path})
    return docs


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split text into overlapping chunks.

    Example with chunk_size=10, overlap=3:
        "ABCDEFGHIJKLMNO" -> ["ABCDEFGHIJ", "HIJKLMNO"]
        The "HIJ" part overlaps so we don't lose context at boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # Move forward by (chunk_size - overlap) so chunks share 'overlap' characters
        start += chunk_size - overlap
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into vector store")
    parser.add_argument(
        "--data-dir",
        default=os.path.join(os.path.dirname(__file__), "data"),
    )
    args = parser.parse_args()

    # Print current settings so user knows what config is being used
    print(f"Configuration:")
    print(f"  Chunk size:    {config.CHUNK_SIZE} chars")
    print(f"  Chunk overlap: {config.CHUNK_OVERLAP} chars")
    print(f"  Retrieval:     TF-IDF + cosine similarity (local, no API needed)\n")

    # Step 1: Load all .txt files from the data directory
    docs = load_documents(args.data_dir)
    print(f"Loaded {len(docs)} documents from {args.data_dir}")

    # Step 2: Split each document into smaller chunks for more precise retrieval
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"], config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['id']}::chunk_{i}",       # unique ID per chunk
                "text": chunk,                           # the actual text content
                "metadata": {"source": doc["source"], "chunk_index": i},  # track where it came from
            })
    print(f"Created {len(all_chunks)} chunks")

    # Step 3: Index all chunks in the vector store (builds TF-IDF + saves to disk)
    store = VectorStore()
    store.add(
        ids=[c["id"] for c in all_chunks],
        documents=[c["text"] for c in all_chunks],
        metadatas=[c["metadata"] for c in all_chunks],
    )
    print(f"Indexed {len(all_chunks)} chunks in vector_store.json")
    print("Done.")


if __name__ == "__main__":
    main()
