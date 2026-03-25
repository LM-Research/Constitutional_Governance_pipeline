from rel_interpreter import load_spec, interpret
from sol import TaskSOL
import json

if __name__ == "__main__":
    raw_input_text = """
    Okay, so the task is pretty clear.
    Task: Write the introduction
    Priority: high
    """

    sl = load_spec()
    rel = interpret(sl, raw_input_text)

    sol = TaskSOL(
        task=rel["task"],
        priority=rel["priority"]
    )

    print(json.dumps(sol.canonical(), indent=2))
