# Evaluation Metrics

**Date:** `RUN_ME`

## Metrics Measured

- **Retrieval Hit Rate**: Does the expected source document appear in retrieved chunks? (0 or 1 per query, averaged)
- **Answer Relevance**: Fraction of expected keywords found in the generated answer (0.0 - 1.0)
- **Latency**: Wall-clock time for retrieve + generate (seconds)
- **Token Count**: Total tokens consumed (prompt + completion)

## Per-Model Results

### gpt-4o-mini

| Question | Hit Rate | Relevance | Latency (s) | Tokens |
|----------|----------|-----------|-------------|--------|
| q1 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q2 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q3 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q4 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q5 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q6 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q7 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q8 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| **AVG** | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |

### gpt-4o

| Question | Hit Rate | Relevance | Latency (s) | Tokens |
|----------|----------|-----------|-------------|--------|
| q1 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q2 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q3 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q4 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q5 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q6 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q7 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| q8 | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| **AVG** | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |

## Model Comparison Summary

| Model | Avg Hit Rate | Avg Relevance | Avg Latency (s) | Avg Tokens |
|-------|-------------|---------------|-----------------|------------|
| gpt-4o-mini | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |
| gpt-4o | `RUN_ME` | `RUN_ME` | `RUN_ME` | `RUN_ME` |

## How to reproduce

```bash
# Must ingest first
python 02_rag_prototype/ingest.py
python 03_evaluation/eval.py
```

## Observations

`RUN_ME` -- add your observations after running the evaluation.
