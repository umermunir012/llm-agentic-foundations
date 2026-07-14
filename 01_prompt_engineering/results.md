# Prompt Engineering Results

**Model:** llama3.2:3b
**Date:** 2026-07-14

## Strategy Comparison

| Strategy | Avg Relevance | Avg Latency (s) | Avg Tokens |
|----------|---------------|-----------------|------------|
| zero_shot | 0.23 | 10.71 | 165 |
| few_shot | 0.49 | 9.01 | 269 |
| chain_of_thought | 0.50 | 22.23 | 361 |
| role_based | 0.56 | 21.93 | 363 |

## How to reproduce

```bash
python 01_prompt_engineering/evaluate_prompts.py
```

Paste the printed table above.

## Observations

- **Role-based prompting scored highest** (0.56 relevance) -- giving the LLM a persona ("aviation safety analyst") helped it focus on domain-relevant keywords.
- **Few-shot and chain-of-thought were close** (0.49 vs 0.50) -- examples and step-by-step reasoning both improved over zero-shot.
- **Zero-shot was weakest** (0.23) -- without guidance, the model often gave generic answers missing key terms.
- **CoT and role-based took ~2x longer** (~22s vs ~10s) -- the model generates more reasoning tokens, which increases latency.
- **Trade-off**: role_based gives the best relevance but at higher latency. For latency-sensitive use, few_shot offers a good balance.
