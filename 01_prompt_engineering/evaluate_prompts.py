"""
Evaluate all prompt strategies on a shared test set.

Usage:
    python 01_prompt_engineering/evaluate_prompts.py

Outputs a markdown table with: strategy, avg relevance (0-1), avg latency (s),
avg tokens used.  Paste the output into results.md.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import STRATEGIES
import config
import llm

MODEL = config.LLM_MODEL

TESTSET = [
    {
        "question": "What is ASRS and who operates it?",
        "keywords": ["aviation safety reporting system", "nasa", "faa"],
    },
    {
        "question": "What are the main contributing factors to controlled flight into terrain (CFIT)?",
        "keywords": ["situational awareness", "terrain", "weather", "approach"],
    },
    {
        "question": "How does the FAA classify aviation incidents vs accidents?",
        "keywords": ["ntsb", "damage", "injury", "49 cfr"],
    },
    {
        "question": "What safety improvements resulted from the Colgan Air 3407 crash?",
        "keywords": ["pilot fatigue", "training", "faa rule", "rest requirements"],
    },
    {
        "question": "Explain the Swiss cheese model of accident causation.",
        "keywords": ["james reason", "layers", "defenses", "holes", "latent"],
    },
]


def keyword_relevance(answer: str, keywords: list[str]) -> float:
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw in answer_lower)
    return hits / len(keywords)


def evaluate_strategy(name: str, prompt_fn) -> dict:
    latencies = []
    token_counts = []
    relevance_scores = []

    for item in TESTSET:
        prompt = prompt_fn(item["question"])
        t0 = time.perf_counter()
        resp = llm.chat(prompt, model=MODEL, max_tokens=300)
        elapsed = time.perf_counter() - t0

        latencies.append(elapsed)
        token_counts.append(resp["total_tokens"])
        relevance_scores.append(keyword_relevance(resp["text"], item["keywords"]))

    n = len(TESTSET)
    return {
        "strategy": name,
        "avg_relevance": sum(relevance_scores) / n,
        "avg_latency_s": sum(latencies) / n,
        "avg_tokens": sum(token_counts) / n,
    }


def main():
    print(f"Model: {MODEL}")
    print(f"Test questions: {len(TESTSET)}\n")

    rows = []
    for name, fn in STRATEGIES.items():
        print(f"  Evaluating {name} ...")
        row = evaluate_strategy(name, fn)
        rows.append(row)

    print("\n| Strategy | Avg Relevance | Avg Latency (s) | Avg Tokens |")
    print("|----------|---------------|-----------------|------------|")
    for r in rows:
        print(
            f"| {r['strategy']} "
            f"| {r['avg_relevance']:.2f} "
            f"| {r['avg_latency_s']:.2f} "
            f"| {r['avg_tokens']:.0f} |"
        )


if __name__ == "__main__":
    main()
