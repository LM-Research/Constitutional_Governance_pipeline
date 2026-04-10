"""
run_example.py
--------------
End-to-end demonstration of the constitutional governance pipeline.

Runs the full governed chain for a single task-domain object:

    SL spec (sl_spec.yaml)
        |
        v
    REL extraction (rel_interpreter.py)
        |
        v
    SOL object (sol.py)
        |
        v
    Canonical output (JSON)

The pipeline is deterministic and fully inspectable. Output is labelled
so that a non-specialist auditor can follow each stage.
"""

import json
import yaml
from rel_interpreter import load_spec, interpret, SpecViolation
from sol import TaskSOL


def divider(title):
    width = 56
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def step(label, value):
    print(f"\n  [{label}]")
    if isinstance(value, dict):
        print(f"  {json.dumps(value, indent=4)}")
    else:
        print(f"  {value}")


# ---------------------------------------------------------------------------
# Example 1: well-formed input
# ---------------------------------------------------------------------------

divider("Example 1: well-formed input")

raw = """
Task: Write the introduction
Priority: high
"""

step("Raw model output", raw.strip())

sl = load_spec()
step("SL spec loaded", sl)

rel = interpret(sl, raw)
step("REL output", rel)

sol = TaskSOL(task=rel["task"], priority=rel["priority"])
step("SOL object", {"task": sol.task, "priority": sol.priority})

canonical = sol.canonical()
step("Canonical output", canonical)


# ---------------------------------------------------------------------------
# Example 2: missing optional field — default applied
# ---------------------------------------------------------------------------

divider("Example 2: missing optional field (priority defaults to 'medium')")

raw2 = """
Task: Review the references
"""

step("Raw model output", raw2.strip())

rel2 = interpret(sl, raw2)
step("REL output", rel2)

sol2 = TaskSOL(task=rel2["task"], priority=rel2["priority"])
step("Canonical output", sol2.canonical())


# ---------------------------------------------------------------------------
# Example 3: missing required field — SpecViolation raised
# ---------------------------------------------------------------------------

divider("Example 3: missing required field — pipeline halts with SpecViolation")

raw3 = """
Priority: low
"""

step("Raw model output", raw3.strip())

try:
    rel3 = interpret(sl, raw3)
except SpecViolation as e:
    step("SpecViolation raised", str(e))
    print("\n  The pipeline does not produce a canonical form.")
    print("  This failure is typed and surfaced explicitly,")
    print("  not silently propagated.")


# ---------------------------------------------------------------------------
# Example 4: invalid enum value — SOL invariant check
# ---------------------------------------------------------------------------

divider("Example 4: invalid priority value — SOL rejects object")

step("Attempting to construct SOL with priority='critical'", "")

try:
    bad_sol = TaskSOL(task="Deploy the model", priority="critical")
except ValueError as e:
    step("ValueError raised", str(e))
    print("\n  The SOL layer enforces typed invariants unconditionally.")
    print("  No object violating the schema can enter the canonical pipeline.")


print(f"\n{'=' * 56}")
print("  All examples complete.")
print(f"{'=' * 56}\n")
