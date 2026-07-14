"""
Shared configuration loaded from environment / .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Ollama, local) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
LLM_MODEL_ALT = os.getenv("LLM_MODEL_ALT", "llama3.2:1b")

# --- Chunking ---
# 512 characters balances context richness with retrieval precision.
# Larger chunks (1024) retain more context but dilute relevance;
# smaller chunks (256) are precise but risk cutting mid-sentence.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))

# 64-char overlap prevents splitting key phrases across chunk boundaries.
# ~12% of chunk size is a common sweet spot.
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
