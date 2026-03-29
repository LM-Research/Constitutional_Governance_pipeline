"""
test_pipeline.py
----------------
Minimal end‑to‑end test for the regex‑based REL front‑end and the SOL layer.

This verifies the governed chain:

    SL → REL_regex → SOL → canonical()

For the task domain, the canonical basis is {task, priority}, so the
canonical projection should preserve both fields exactly.
"""

from rel_interpreter import load_spec, interpret
from sol import TaskSOL


def test_end_to_end_pipeline():
    raw_text = """
    Task: Write the introduction
    Priority: high
    """

    # Load the regex‑based SL spec
    sl = load_spec()

    # REL_regex extraction
    rel = interpret(sl, raw_text)

    # Construct SOL object
    sol = TaskSOL(
        task=rel["task"],
        priority=rel["priority"],
    )

    # Canonical projection must match the expected dict
    assert sol.canonical() == {
        "task": "Write the introduction",
        "priority": "high",
    }
