from rel_interpreter import load_spec, interpret
from sol import TaskSOL

def test_end_to_end_pipeline():
    raw_text = """
    Task: Write the introduction
    Priority: high
    """

    sl = load_spec()
    rel = interpret(sl, raw_text)

    sol = TaskSOL(
        task=rel["task"],
        priority=rel["priority"]
    )

    assert sol.canonical() == {
        "task": "Write the introduction",
        "priority": "high"
    }
