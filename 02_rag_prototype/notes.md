# RAG Prototype Notes

## Architecture

```
.txt files -> chunk (character-based) -> TF-IDF index -> retrieve (cosine similarity) -> Ollama LLM generate
```

All components run locally. No API keys or cloud services needed.

## Design Decisions

### Chunk Size: 512 characters (default)
- Balances retrieval precision with sufficient context.
- Aviation incident reports have natural paragraph-level structure (~200-600 chars).
- Smaller chunks (256) fragment report sections; larger chunks (1024) dilute relevance when retrieving specific facts.

### Chunk Overlap: 64 characters (default)
- ~12% of chunk size prevents splitting key phrases at boundaries.
- Aviation reports contain multi-sentence findings where meaning depends on adjacent sentences.

### Retrieval: TF-IDF + Cosine Similarity
- For a small corpus (5 documents, 20 chunks), TF-IDF is simple, fast, and effective.
- No embedding model or API calls needed -- runs instantly with zero dependencies.
- Stored in `vector_store.json` for persistence.
- For production or larger corpora, swap in a proper vector DB (ChromaDB, FAISS) with dense embeddings.

### LLM: Ollama (local)
- `llama3.2:3b` -- good quality-to-speed ratio, runs in ~4 GB RAM.
- `llama3.2:1b` -- faster, lighter, used as comparison model in evaluation.
- No API costs. Runs entirely on CPU (GPU optional for speed).

### Top-K Retrieval: 3
- The corpus is small (5 documents, ~20 chunks). 3 chunks provide enough context without exceeding the LLM's useful attention window.

## How to Run

```bash
# 1. Ingest documents
python 02_rag_prototype/ingest.py

# 2. Query
python 02_rag_prototype/query.py "What caused the Colgan Air crash?"
```
