"""
Thin wrapper around Ollama's REST API. No SDK needed -- just requests.

Ollama runs LLMs locally on your machine and exposes a REST API at localhost:11434.
This module provides two functions:
  - chat()       : single prompt -> response (for simple queries)
  - chat_multi() : full conversation history -> response (for the agent loop)
"""

import requests
import config


def chat(prompt: str, system: str = "", model: str | None = None, max_tokens: int = 500) -> dict:
    """
    Send a single prompt to Ollama and get a response.

    Args:
        prompt:     The user's question/instruction
        system:     Optional system prompt (sets the AI's role/behavior)
        model:      Which Ollama model to use (defaults to config.LLM_MODEL)
        max_tokens: Maximum length of the response

    Returns:
        dict with: text, model, prompt_tokens, completion_tokens, total_tokens
    """
    model = model or config.LLM_MODEL

    # Build the messages list (OpenAI-style format that Ollama also uses)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Call Ollama's local REST API
    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,  # get full response at once (not streamed token by token)
            "options": {
                "num_predict": max_tokens,  # max output tokens
                "temperature": 0.0,         # deterministic output (no randomness)
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    # Extract the response and token counts
    return {
        "text": data["message"]["content"],
        "model": model,
        "prompt_tokens": data.get("prompt_eval_count", 0),      # tokens in the input
        "completion_tokens": data.get("eval_count", 0),          # tokens in the output
        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
    }


def chat_multi(messages: list[dict], system: str = "", model: str | None = None, max_tokens: int = 500) -> dict:
    """
    Chat with full message history -- used by the agent for multi-turn conversations.

    Args:
        messages:   List of {"role": "user"/"assistant", "content": "..."} dicts
        system:     Optional system prompt
        model:      Which Ollama model to use
        max_tokens: Maximum response length

    Returns:
        Same dict format as chat()
    """
    model = model or config.LLM_MODEL

    # Prepend system message if provided
    all_msgs = []
    if system:
        all_msgs.append({"role": "system", "content": system})
    all_msgs.extend(messages)

    resp = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": model,
            "messages": all_msgs,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.0},
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "text": data["message"]["content"],
        "model": model,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "completion_tokens": data.get("eval_count", 0),
        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
    }
