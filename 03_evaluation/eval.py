"""
Evaluation script: measures retrieval hit rate, answer relevance, latency,
and token count for the RAG pipeline. Compares >=2 Ollama models.

Metrics explained:
  - Hit Rate:   Did the retriever find the correct source document? (0 or 1)
  - Relevance:  What fraction of expected keywords appear in the answer? (0.0 - 1.0)
  - Latency:    How long did retrieval + generation take? (seconds)
  - Tokens:     How many tokens were consumed? (input + output)

Usage:
    python 03_evaluation/eval.py

Outputs markdown tables. Paste results into metrics.md.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Import the RAG functions we're evaluating
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "02_rag_prototype"))
from query import retrieve, generate_answer, get_store


def load_testset() -> list[dict]:
    """Load test questions from testset.json (each has expected keywords and source)."""
    path = os.path.join(os.path.dirname(__file__), "testset.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieval_hit_rate(retrieved_chunks: list[dict], expected_source: str) -> float:
    """Did the retriever find the right document? Returns 1.0 if yes, 0.0 if no."""
    for chunk in retrieved_chunks:
        source = chunk.get("metadata", {}).get("source", "")
        if expected_source in source:
            return 1.0
    return 0.0


def keyword_relevance(answer: str, keywords: list[str]) -> float:
    """What fraction of expected keywords appear in the answer? (0.0 to 1.0)"""
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return hits / len(keywords) if keywords else 0.0


def evaluate_model(model_name: str, testset: list[dict], store) -> list[dict]:
    """Run all test questions through the RAG pipeline with a specific model."""
    results = []
    for item in testset:
        # Time the full retrieve + generate pipeline
        t0 = time.perf_counter()
        retrieved = retrieve(item["question"], store)
        gen = generate_answer(item["question"], retrieved, model=model_name)
        elapsed = time.perf_counter() - t0

        # Score this question
        hit = retrieval_hit_rate(retrieved, item["expected_source"])
        relevance = keyword_relevance(gen["answer"], item["expected_keywords"])

        results.append({
            "id": item["id"],
            "hit": hit,
            "relevance": relevance,
            "latency_s": elapsed,
            "total_tokens": gen["total_tokens"],
            "input_tokens": gen["input_tokens"],
            "output_tokens": gen["output_tokens"],
        })
    return results


def print_model_results(model: str, results: list[dict]):
    """Print a markdown table of per-question results + averages."""
    n = len(results)
    avg_hit = sum(r["hit"] for r in results) / n
    avg_rel = sum(r["relevance"] for r in results) / n
    avg_lat = sum(r["latency_s"] for r in results) / n
    avg_tok = sum(r["total_tokens"] for r in results) / n

    print(f"\n### {model}\n")
    print("| Question | Hit Rate | Relevance | Latency (s) | Tokens |")
    print("|----------|----------|-----------|-------------|--------|")
    for r in results:
        print(
            f"| {r['id']} | {r['hit']:.0f} | {r['relevance']:.2f} "
            f"| {r['latency_s']:.2f} | {r['total_tokens']} |"
        )
    print("|----------|----------|-----------|-------------|--------|")
    print(f"| **AVG** | **{avg_hit:.2f}** | **{avg_rel:.2f}** | **{avg_lat:.2f}** | **{avg_tok:.0f}** |")


def main():
    # Compare these two models (configured in .env)
    models = [config.LLM_MODEL, config.LLM_MODEL_ALT]

    testset = load_testset()
    print(f"Test set: {len(testset)} questions")
    print(f"Models: {', '.join(models)}\n")

    # Load the vector store (must run ingest.py first)
    store = get_store()

    # Evaluate each model and collect summary stats
    summary = []
    for model in models:
        print(f"Evaluating {model} ...")
        results = evaluate_model(model, testset, store)
        print_model_results(model, results)

        n = len(results)
        summary.append({
            "model": model,
            "avg_hit": sum(r["hit"] for r in results) / n,
            "avg_rel": sum(r["relevance"] for r in results) / n,
            "avg_lat": sum(r["latency_s"] for r in results) / n,
            "avg_tok": sum(r["total_tokens"] for r in results) / n,
        })

    # Print side-by-side comparison of all models
    print("\n## Model Comparison Summary\n")
    print("| Model | Avg Hit Rate | Avg Relevance | Avg Latency (s) | Avg Tokens |")
    print("|-------|-------------|---------------|-----------------|------------|")
    for s in summary:
        print(
            f"| {s['model']} | {s['avg_hit']:.2f} | {s['avg_rel']:.2f} "
            f"| {s['avg_lat']:.2f} | {s['avg_tok']:.0f} |"
        )


if __name__ == "__main__":
    main()
