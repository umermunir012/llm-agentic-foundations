# Evaluation Metrics

**Date:** 2026-07-14

## Metrics Measured

- **Retrieval Hit Rate**: Does the expected source document appear in retrieved chunks? (0 or 1 per query, averaged)
- **Answer Relevance**: Fraction of expected keywords found in the generated answer (0.0 - 1.0)
- **Latency**: Wall-clock time for retrieve + generate (seconds)
- **Token Count**: Total tokens consumed (prompt + completion)

## Per-Model Results

### llama3.2:3b

| Question | Hit Rate | Relevance | Latency (s) | Tokens |
|----------|----------|-----------|-------------|--------|
| q1 | 1 | 0.75 | 15.03 | 539 |
| q2 | 1 | 0.75 | 13.72 | 505 |
| q3 | 1 | 0.00 | 17.41 | 565 |
| q4 | 1 | 1.00 | 10.91 | 393 |
| q5 | 1 | 0.75 | 11.56 | 451 |
| q6 | 1 | 0.50 | 14.34 | 522 |
| q7 | 1 | 0.50 | 11.70 | 420 |
| q8 | 1 | 0.40 | 13.37 | 439 |
|----------|----------|-----------|-------------|--------|
| **AVG** | **1.00** | **0.58** | **13.50** | **479** |

### llama3.2:1b

| Question | Hit Rate | Relevance | Latency (s) | Tokens |
|----------|----------|-----------|-------------|--------|
| q1 | 1 | 0.75 | 12.13 | 504 |
| q2 | 1 | 0.75 | 8.11 | 490 |
| q3 | 1 | 0.25 | 13.91 | 645 |
| q4 | 1 | 0.67 | 9.09 | 443 |
| q5 | 1 | 0.75 | 6.41 | 423 |
| q6 | 1 | 0.50 | 9.27 | 533 |
| q7 | 1 | 0.00 | 7.86 | 430 |
| q8 | 1 | 0.60 | 9.48 | 464 |
|----------|----------|-----------|-------------|--------|
| **AVG** | **1.00** | **0.53** | **9.53** | **492** |

## Model Comparison Summary

| Model | Avg Hit Rate | Avg Relevance | Avg Latency (s) | Avg Tokens |
|-------|-------------|---------------|-----------------|------------|
| llama3.2:3b | 1.00 | 0.58 | 13.50 | 479 |
| llama3.2:1b | 1.00 | 0.53 | 9.53 | 492 |

## How to reproduce

```bash
# Must ingest first
python 02_rag_prototype/ingest.py
python 03_evaluation/eval.py
```

## Observations

- **Retrieval hit rate is perfect (1.00)** for both models -- TF-IDF reliably finds the correct source document for all 8 test questions in this small corpus.
- **3b model has slightly better relevance** (0.58 vs 0.53) -- the larger model produces answers with more expected keywords.
- **1b model is ~30% faster** (9.53s vs 13.50s avg) -- significant for interactive use.
- **Token counts are similar** (~479 vs ~492) -- both models generate comparable-length answers.
- **Trade-off**: the 3b model's quality edge is modest (+0.05 relevance) for ~4s extra latency. For this corpus, the 1b model is a reasonable choice if speed matters.
