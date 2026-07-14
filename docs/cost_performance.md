# Cost & Performance Analysis

## Local vs Cloud: Why This Project Uses Ollama

This project runs **fully local** via Ollama. There are no API costs. Below is a comparison to help understand the trade-offs.

## Cloud API Pricing (for reference)

| Model | Input ($/1M tokens) | Output ($/1M tokens) | Notes |
|-------|---------------------|----------------------|-------|
| gpt-4o-mini | $0.15 | $0.60 | Cheapest cloud option |
| gpt-4o | $2.50 | $10.00 | ~17x cost of mini |
| Claude Sonnet | $3.00 | $15.00 | Anthropic equivalent |
| Claude Haiku | $0.25 | $1.25 | Fast & cheap |
| **Ollama (local)** | **$0.00** | **$0.00** | **Hardware cost only** |

## Local Model Comparison

| Model | Size | RAM Needed | Speed (tokens/sec on CPU) | Quality |
|-------|------|-----------|--------------------------|---------|
| llama3.2:1b | 1.3 GB | ~2 GB | ~20-30 t/s | Basic, sometimes misses nuance |
| llama3.2:3b | 2.0 GB | ~4 GB | ~10-18 t/s | Good for most tasks |
| llama3.1:8b | 4.7 GB | ~8 GB | ~5-10 t/s | Best local quality |

## Trade-offs: Size vs Latency vs Cost vs Accuracy

| Factor | Small (1B) | Medium (3B) | Large (8B) | Cloud API |
|--------|-----------|-------------|------------|-----------|
| Latency | Low (~2-5s) | Medium (~5-15s) | High (~10-30s) | Medium (~1-3s) |
| Cost | $0 | $0 | $0 | $0.001-0.05/query |
| Accuracy | Lower | Good | Better | Best |
| Privacy | Full | Full | Full | Data leaves machine |
| Offline | Yes | Yes | Yes | No |

## Estimated Token Usage Per Pipeline Run

### Ingestion
- **Cost: $0** (TF-IDF indexing is local, no LLM calls)

### Single RAG Query
- ~400-600 input tokens (context + question)
- ~100-200 output tokens (answer)
- **Cost: $0 local**, ~$0.0003 with gpt-4o-mini

### Prompt Engineering Eval (4 strategies x 5 questions = 20 calls)
- ~3,000-5,000 total tokens
- **Cost: $0 local**, ~$0.005 with gpt-4o-mini

### Full Evaluation (8 questions x 2 models = 16 calls)
- ~8,000-12,000 total tokens
- **Cost: $0 local**, ~$0.04 with cloud APIs

### Agent Run (typically 2-4 steps)
- ~1,500-3,000 total tokens (context grows each step)
- **Cost: $0 local**, ~$0.002 with gpt-4o-mini

## When to Use Local vs Cloud

| Use Case | Recommendation |
|----------|---------------|
| Learning & prototyping | Local (Ollama) -- free, private, no rate limits |
| Small corpus RAG | Local works well |
| Production with quality requirements | Cloud APIs (gpt-4o, Claude Sonnet) |
| Sensitive/private data | Local only |
| High throughput (1000s of queries) | Cloud APIs (faster, parallelizable) |

## Actual Performance

Tested on HP ProBook (Intel Ultra 7 155U, 16 GB RAM, CPU-only inference):

- **llama3.2:3b**: ~13.5s avg per RAG query, 0.58 avg keyword relevance
- **llama3.2:1b**: ~9.5s avg per RAG query, 0.53 avg keyword relevance
- **Prompt engineering**: role-based prompting scored highest (0.56) but took ~22s; zero-shot was fastest (~11s) but weakest (0.23)
- **Agent runs**: 3-6 steps, ~30-90s total depending on tool count
- **Verdict**: the 3b model's quality edge is modest (+5% relevance) for ~40% more latency. For this corpus size, the 1b model is adequate for prototyping. The 3b model is better for final results where accuracy matters more than speed.
