"""
test_pipeline.py
----------------
Minimal end-to-end test for the governed chain:

    SL spec → REL extraction → SOL object → canonical()

Verifies that a well-formed input passes through all three stages and
produces the expected canonical dict.
"""

from rel_interpreter import load_spec, interpret
from sol import TaskSOL


def test_end_to_end_pipeline() -> None:
    raw_text = """
    Task: Write the introduction
    Priority: high
    """

    sl = load_spec()
    rel = interpret(sl, raw_text)

    # Required fields must be present; assert before constructing SOL.
    assert rel["task"] is not None, "REL must extract required field: task"
    assert rel["priority"] is not None, "REL must extract required field: priority"

    sol = TaskSOL(
        task=rel["task"],
        priority=rel["priority"],
    )

    assert sol.canonical() == {
        "task": "Write the introduction",
        "priority": "high",
    }