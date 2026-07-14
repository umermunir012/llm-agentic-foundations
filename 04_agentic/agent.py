"""
Hand-rolled ReAct agent for aviation safety queries.

ReAct = Reasoning + Acting. The agent follows a loop:
  1. THOUGHT:      "I need to find out X..."
  2. ACTION:       calls a tool (calculator, RAG lookup, weather API)
  3. OBSERVATION:  receives the tool's output
  4. Repeat until it has enough info, then gives a FINAL ANSWER

This is built from scratch -- no LangChain or LlamaIndex.

Usage:
    python 04_agentic/agent.py "How many wildlife strikes per year, and what is that per day?"
    python 04_agentic/agent.py "What is the current weather at the airport where Asiana 214 crashed?"
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import llm
from tools import TOOLS, get_tool_descriptions

MAX_STEPS = 8  # safety limit to prevent infinite loops


def build_system_prompt() -> str:
    """Build the system prompt that tells the LLM how to use tools."""
    tool_desc = get_tool_descriptions()
    return f"""You are an aviation safety research assistant with access to tools.

You follow a strict Thought -> Action -> Observation loop.

Available tools:
{tool_desc}

## Response format

At each step, respond with EXACTLY one of:

1. A Thought + Action:
Thought: <your reasoning about what to do next>
Action: <tool_name>(<input>)

2. A final answer (when you have enough information):
Thought: <your final reasoning>
Final Answer: <your complete answer to the user>

Rules:
- Always start with a Thought.
- Call only ONE tool per step.
- Tool input is a single string argument in parentheses.
- After receiving an Observation, continue reasoning.
- If a tool call fails, reason about why and try an alternative.
- Always give a Final Answer -- do not loop forever."""


def parse_action(text: str) -> tuple[str | None, str | None]:
    """Extract tool name and input from the LLM's response.
    Example: 'Action: calculator(17000 / 365)' -> ('calculator', '17000 / 365')
    """
    match = re.search(r"Action:\s*(\w+)\((.+?)\)\s*$", text, re.MULTILINE | re.DOTALL)
    if match:
        tool_name = match.group(1).strip()
        tool_input = match.group(2).strip().strip("\"'")
        return tool_name, tool_input
    return None, None


def parse_final_answer(text: str) -> str | None:
    """Extract the final answer if the LLM has decided it's done reasoning."""
    match = re.search(r"Final Answer:\s*(.+)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def run_agent(question: str, verbose: bool = True) -> dict:
    """
    Run the ReAct agent loop.

    The loop works like this:
      1. Send the conversation so far to the LLM
      2. LLM responds with a Thought + Action (or Final Answer)
      3. We execute the action (call the tool)
      4. We feed the tool's output back as an Observation
      5. Repeat until Final Answer or MAX_STEPS reached
    """
    system_prompt = build_system_prompt()
    messages = [{"role": "user", "content": question}]
    trace = []  # record of every step for debugging

    for step in range(1, MAX_STEPS + 1):
        # Ask the LLM what to do next (it sees the full conversation history)
        resp = llm.chat_multi(messages, system=system_prompt, max_tokens=500)
        assistant_text = resp["text"]
        messages.append({"role": "assistant", "content": assistant_text})

        if verbose:
            print(f"\n--- Step {step} ---")
            print(assistant_text)

        # Check if the LLM gave a final answer (we're done!)
        final = parse_final_answer(assistant_text)
        if final:
            trace.append({"step": step, "type": "final_answer", "content": final})
            return {"answer": final, "trace": trace, "steps": step}

        # Try to parse which tool the LLM wants to call
        tool_name, tool_input = parse_action(assistant_text)

        if tool_name is None:
            # LLM didn't follow the format -- ask it to try again
            observation = (
                "Error: Could not parse your action. Please use the format: "
                "Action: tool_name(\"input\")"
            )
            trace.append({"step": step, "type": "parse_error", "content": assistant_text})

        elif tool_name not in TOOLS:
            # LLM tried to use a tool that doesn't exist
            observation = (
                f"Error: Unknown tool '{tool_name}'. "
                f"Available tools: {', '.join(TOOLS.keys())}"
            )
            trace.append({
                "step": step, "type": "error",
                "action": f"{tool_name}({tool_input})",
                "observation": observation,
            })

        else:
            # Execute the tool and capture its output
            try:
                result = TOOLS[tool_name]["function"](tool_input)
                observation = result
                trace.append({
                    "step": step, "type": "action",
                    "action": f"{tool_name}({tool_input})",
                    "observation": observation,
                })
            except Exception as e:
                # Tool crashed -- tell the LLM what went wrong
                observation = f"Error executing {tool_name}: {e}"
                trace.append({
                    "step": step, "type": "tool_error",
                    "action": f"{tool_name}({tool_input})",
                    "observation": observation,
                })

        if verbose:
            print(f"Observation: {observation[:300]}{'...' if len(observation) > 300 else ''}")

        # Feed the tool's output back to the LLM as the next user message
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    # Reached max steps without a final answer -- safety exit
    return {
        "answer": "Agent reached maximum steps without producing a final answer.",
        "trace": trace,
        "steps": MAX_STEPS,
    }


def main():
    parser = argparse.ArgumentParser(description="ReAct Agent for aviation safety")
    parser.add_argument("question", help="Your question")
    parser.add_argument("--quiet", action="store_true", help="Suppress step-by-step output")
    args = parser.parse_args()

    result = run_agent(args.question, verbose=not args.quiet)

    # Print final summary
    print(f"\n{'='*60}")
    print(f"Final Answer: {result['answer']}")
    print(f"Steps taken: {result['steps']}")
    print(f"{'='*60}")

    # Print trace showing which tools were called
    print("\nTrace:")
    for entry in result["trace"]:
        step = entry["step"]
        if entry["type"] == "action":
            print(f"  [{step}] {entry['action']}")
        elif entry["type"] == "final_answer":
            print(f"  [{step}] -> Final Answer")
        else:
            print(f"  [{step}] {entry['type']}: {entry.get('content', entry.get('observation', ''))[:80]}")


if __name__ == "__main__":
    main()
