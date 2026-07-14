"""
Tool definitions for the ReAct agent.

Three tools:
  1. calculator   - evaluate arithmetic expressions
  2. rag_lookup   - query the aviation safety RAG system
  3. weather_metar - fetch current METAR weather for an airport (external API)
"""

import os
import sys
import re

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# -------------------------------------------------------------------
# Tool 1: Calculator
# -------------------------------------------------------------------
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    Supports: +, -, *, /, **, (), and numeric values.
    """
    # Allow only safe characters
    sanitized = re.sub(r"[^0-9+\-*/().%\s]", "", expression)
    if not sanitized.strip():
        return "Error: empty or invalid expression"
    try:
        result = eval(sanitized, {"__builtins__": {}}, {})  # noqa: S307 - sandboxed
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# -------------------------------------------------------------------
# Tool 2: RAG Lookup
# -------------------------------------------------------------------
def rag_lookup(question: str) -> str:
    """
    Query the aviation safety RAG system and return the answer.
    Requires that documents have been ingested first (02_rag_prototype/ingest.py).
    """
    try:
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "02_rag_prototype",
        ))
        from query import rag_query
        result = rag_query(question)
        return result["answer"]
    except Exception as e:
        return f"Error querying RAG system: {e}"


# -------------------------------------------------------------------
# Tool 3: Weather METAR (external API - aviationweather.gov)
# -------------------------------------------------------------------
def weather_metar(station_id: str) -> str:
    """
    Fetch the current METAR weather observation for an airport.
    station_id: ICAO airport code (e.g., KJFK, KLAX, EGLL).
    Uses the public aviationweather.gov API (no key required).
    """
    url = (
        "https://aviationweather.gov/api/data/metar"
        f"?ids={station_id.upper()}&format=raw&taf=false"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        text = resp.text.strip()
        if not text:
            return f"No METAR data found for station '{station_id}'. Check the ICAO code."
        return text
    except requests.RequestException as e:
        return f"Error fetching METAR for {station_id}: {e}"


# -------------------------------------------------------------------
# Tool registry
# -------------------------------------------------------------------
TOOLS = {
    "calculator": {
        "function": calculator,
        "description": (
            "Evaluate a math expression. Input: a mathematical expression string "
            "(e.g., '(3 + 5) * 2'). Returns the numeric result."
        ),
    },
    "rag_lookup": {
        "function": rag_lookup,
        "description": (
            "Look up aviation safety information from the incident report database. "
            "Input: a natural language question about aviation safety. "
            "Returns an answer based on indexed NTSB/ASRS/FAA reports."
        ),
    },
    "weather_metar": {
        "function": weather_metar,
        "description": (
            "Get current METAR weather observation for an airport. "
            "Input: an ICAO airport code (e.g., 'KJFK'). "
            "Returns the raw METAR string."
        ),
    },
}


def get_tool_descriptions() -> str:
    """Format tool descriptions for inclusion in the agent system prompt."""
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}: {info['description']}")
    return "\n".join(lines)
