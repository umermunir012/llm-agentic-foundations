"""
RAG query pipeline: retrieve from vector store -> generate answer via Ollama.

RAG = Retrieval-Augmented Generation:
  1. User asks a question
  2. We find the most relevant document chunks (retrieval)
  3. We send those chunks + the question to the LLM (generation)
  4. The LLM answers based on the provided context

Usage:
    python 02_rag_prototype/query.py "What caused the Colgan Air crash?"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import llm
from vector_store import VectorStore

TOP_K = 3  # number of chunks to retrieve per query


def get_store() -> VectorStore:
    """Load the vector store from disk, or exit with an error if it doesn't exist."""
    store = VectorStore()
    if not store.load():
        print("ERROR: Vector store not found. Run ingestion first:")
        print("  python 02_rag_prototype/ingest.py")
        sys.exit(1)
    return store


def retrieve(question: str, store: VectorStore, top_k: int = TOP_K) -> list[dict]:
    """Find the top-k most relevant chunks for the question using TF-IDF similarity."""
    results = store.query(question, n_results=top_k)
    retrieved = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append({"text": doc, "metadata": meta, "distance": dist})
    return retrieved


def generate_answer(question: str, context_chunks: list[dict], model: str | None = None) -> dict:
    """Send retrieved context + question to the LLM and get an answer."""
    model = model or config.LLM_MODEL

    # Combine all retrieved chunks into one context string, separated by dividers
    context = "\n\n---\n\n".join(c["text"] for c in context_chunks)

    # System prompt tells the LLM how to behave
    system_msg = (
        "You are an aviation safety expert. Answer the user's question using ONLY "
        "the provided context. If the context doesn't contain enough information, "
        "say so. Cite the source document when possible."
    )

    # User message includes the context and the actual question
    user_msg = f"Context:\n{context}\n\nQuestion: {question}"

    # Call the local LLM via Ollama
    resp = llm.chat(user_msg, system=system_msg, model=model, max_tokens=500)

    return {
        "answer": resp["text"],
        "model": resp["model"],
        "input_tokens": resp["prompt_tokens"],
        "output_tokens": resp["completion_tokens"],
        "total_tokens": resp["total_tokens"],
    }


def rag_query(question: str, model: str | None = None) -> dict:
    """Full RAG pipeline: retrieve relevant chunks, then generate an answer."""
    store = get_store()
    retrieved = retrieve(question, store)
    result = generate_answer(question, retrieved, model)
    result["retrieved_chunks"] = retrieved
    return result


def main():
    parser = argparse.ArgumentParser(description="Query the RAG system")
    parser.add_argument("question", help="Your question about aviation safety")
    args = parser.parse_args()

    result = rag_query(args.question)

    # Display results
    print(f"\nQuestion: {args.question}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nModel: {result['model']}")
    print(f"Tokens: {result['total_tokens']} (input: {result['input_tokens']}, output: {result['output_tokens']})")
    print(f"\nRetrieved {len(result['retrieved_chunks'])} chunks:")
    for i, chunk in enumerate(result["retrieved_chunks"]):
        print(f"  [{i+1}] distance={chunk['distance']:.4f}  source={chunk['metadata'].get('source', 'N/A')}")


if __name__ == "__main__":
    main()
