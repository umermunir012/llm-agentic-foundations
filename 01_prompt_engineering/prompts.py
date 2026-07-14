"""
Prompt variants for aviation safety incident report analysis.

Four strategies: zero-shot, few-shot, chain-of-thought, role-based.
Each returns a formatted prompt string given a user question.
"""

# ---------------------------------------------------------------------------
# Zero-shot: no examples, just the instruction
# ---------------------------------------------------------------------------
def zero_shot(question: str) -> str:
    return (
        "Answer the following question about aviation safety incidents "
        "concisely and accurately.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )


# ---------------------------------------------------------------------------
# Few-shot: 3 exemplar Q&A pairs before the real question
# ---------------------------------------------------------------------------
FEW_SHOT_EXAMPLES = [
    {
        "q": "What is the most common cause of runway incursions?",
        "a": "Pilot deviation, where a pilot enters a runway without ATC clearance, "
             "accounts for the majority of runway incursions according to FAA data.",
    },
    {
        "q": "How are bird strikes reported?",
        "a": "Pilots and airport personnel file reports through the FAA Wildlife Strike "
             "Database (FAA Form 5200-7) within 24 hours of the event.",
    },
    {
        "q": "What does ASRS stand for?",
        "a": "ASRS stands for the Aviation Safety Reporting System, a voluntary "
             "confidential reporting program run by NASA on behalf of the FAA.",
    },
]


def few_shot(question: str) -> str:
    examples = "\n\n".join(
        f"Q: {e['q']}\nA: {e['a']}" for e in FEW_SHOT_EXAMPLES
    )
    return (
        "You are an aviation safety expert. Below are example Q&A pairs. "
        "Follow the same style to answer the final question.\n\n"
        f"{examples}\n\n"
        f"Q: {question}\n"
        "A:"
    )


# ---------------------------------------------------------------------------
# Chain-of-thought: instruct the model to reason step-by-step
# ---------------------------------------------------------------------------
def chain_of_thought(question: str) -> str:
    return (
        "You are an aviation safety analyst. Answer the question below by "
        "first reasoning step-by-step, then giving a concise final answer.\n\n"
        f"Question: {question}\n\n"
        "Step-by-step reasoning:\n"
        "1."
    )


# ---------------------------------------------------------------------------
# Role-based: assign a specific expert persona
# ---------------------------------------------------------------------------
def role_based(question: str) -> str:
    return (
        "You are a senior NTSB investigator with 20 years of experience "
        "analyzing aviation accidents and incidents. You base your answers "
        "on official NTSB and FAA data, citing report numbers when possible.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )


# ---------------------------------------------------------------------------
# Registry for programmatic access
# ---------------------------------------------------------------------------
STRATEGIES = {
    "zero_shot": zero_shot,
    "few_shot": few_shot,
    "chain_of_thought": chain_of_thought,
    "role_based": role_based,
}
