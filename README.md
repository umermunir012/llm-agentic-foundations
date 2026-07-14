# LLM Customization & Agentic AI Foundations

A hands-on repository demonstrating core LLM application patterns applied to **aviation safety incident reports**: prompt engineering, retrieval-augmented generation (RAG), evaluation, and agentic AI.

Runs **fully local** using [Ollama](https://ollama.com) -- no API keys or cloud costs required.

## Repository Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
├── config.py                          # Shared configuration
├── llm.py                            # Ollama API wrapper
├── vector_store.py                   # TF-IDF vector store (no external deps)
├── 01_prompt_engineering/
│   ├── prompts.py                     # 4 prompt strategies (zero-shot, few-shot, CoT, role-based)
│   ├── evaluate_prompts.py            # Score all strategies on a shared test set
│   └── results.md                     # Results table (RUN_ME placeholders)
├── 02_rag_prototype/
│   ├── ingest.py                      # Chunk -> index -> store in vector_store.json
│   ├── query.py                       # Retrieve -> generate answer
│   ├── data/                          # Sample NTSB/ASRS/FAA documents (5 reports)
│   └── notes.md                       # Design decisions & rationale
├── 03_evaluation/
│   ├── eval.py                        # Retrieval hit rate, relevance, latency, tokens
│   ├── testset.json                   # 8 test questions with expected keywords/sources
│   └── metrics.md                     # Results tables (RUN_ME placeholders)
├── 04_agentic/
│   ├── tools.py                       # 3 tools: calculator, RAG lookup, METAR weather API
│   ├── agent.py                       # Hand-rolled ReAct loop (no LangChain)
│   └── traces.md                      # Agent trace outputs (RUN_ME placeholders)
└── docs/
    └── cost_performance.md            # Cost estimates and performance notes
```

## Quick Start

### 1. Prerequisites

Install [Ollama](https://ollama.com) and pull models:

```bash
ollama pull llama3.2:3b
ollama pull llama3.2:1b
```

### 2. Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

### 3. Ingest Documents

```bash
python 02_rag_prototype/ingest.py
```

This chunks the 5 sample aviation reports and indexes them in `vector_store.json` using TF-IDF.

### 4. Run Each Module

```bash
# Prompt engineering evaluation
python 01_prompt_engineering/evaluate_prompts.py

# RAG query (interactive)
python 02_rag_prototype/query.py "What caused the Colgan Air crash?"

# Full evaluation (compares llama3.2:3b vs llama3.2:1b)
python 03_evaluation/eval.py

# Agentic ReAct loop
python 04_agentic/agent.py "How many wildlife strikes happen per year and what is that per day?"
python 04_agentic/agent.py "What is the current weather at the airport where Asiana 214 crashed?"
```

### 5. Paste Results

All `results.md`, `metrics.md`, and `traces.md` files contain `RUN_ME` placeholders. After running the scripts, paste the printed output into the corresponding markdown files.

## Configuration

All defaults are configurable via environment variables (see `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_MODEL` | `llama3.2:3b` | Primary LLM model |
| `LLM_MODEL_ALT` | `llama3.2:1b` | Comparison model for evaluation |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Character overlap between chunks |

## Domain: Aviation Safety

The sample data includes:
- **NTSB accident reports**: Colgan Air 3407, Asiana 214, Comair 5191
- **ASRS voluntary report**: altitude deviation incident
- **FAA advisory circular**: wildlife strike reporting guidance

## Design Decisions

See [02_rag_prototype/notes.md](02_rag_prototype/notes.md) for RAG parameter rationale and [docs/cost_performance.md](docs/cost_performance.md) for cost analysis.

### Why hand-rolled ReAct instead of LangChain?

The agent in `04_agentic/` implements the ReAct (Reasoning + Acting) pattern from scratch:
1. **Transparency**: every step is visible in the trace -- no framework magic
2. **Debuggability**: you can see exactly what prompt the LLM receives at each step
3. **Simplicity**: ~150 lines of Python, no dependency graph to learn
4. **Educational value**: understanding the loop matters more than framework fluency

### Why TF-IDF instead of vector embeddings?

For a small corpus (5 documents, 20 chunks), TF-IDF with cosine similarity provides effective retrieval with zero dependencies and no API calls. For production or larger corpora, swap in ChromaDB or FAISS with proper embedding models.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com) with at least one model pulled
- Internet access (only for the METAR weather tool in the agent)
