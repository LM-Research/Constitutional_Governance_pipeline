"""
run_example.py
--------------
End-to-end demonstration of the constitutional governance pipeline.

Runs three scenarios through the full governed chain:

    SL → REL → SOL → Norm → ε → Sanitize → Canon → Collapse → Trace

Example 1: Task domain (original minimal example, retained for continuity)
Example 2a: Credit-scoring domain — clean object (income + credit_score)
Example 2b: Credit-scoring domain — proxy (zip_code) + drift (latent_cluster)
Example 2c: Credit-scoring domain — object that produces ⊥ (negative income)

Output is printed in a format readable by a non-specialist auditor:
each stage is labelled, pruning decisions are explained, and the final
trace audit report is printed in full.
"""

from __future__ import annotations

import json
import yaml

from rel_compiler import RELCompiler, RELFailure
from sol import TaskSOL, CreditSOL
from pipeline import collapse
from trace import ConstitutionalTrace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _divider(title: str) -> None:
    width = 64
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def _step(label: str, value: object) -> None:
    print(f"\n  [{label}]")
    if isinstance(value, dict):
        print(f"  {json.dumps(value, indent=4, default=str)}")
    else:
        print(f"  {value}")


def _strip_provenance(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _print_trace(trace: ConstitutionalTrace) -> None:
    report = trace.audit_report()
    print(f"\n  Trace summary:")
    print(f"    domain         : {report['domain']}")
    print(f"    schema_version : {report['schema_version']}")
    print(f"    total events   : {report['total_events']}")
    print(f"    commits        : {report['commits']}")
    print(f"    failures/violations: {report['failures']}")
    print()
    for i, entry in enumerate(report["entries"]):
        status = "✓ COMMIT" if entry["op"] == "COMMIT" else f"✗ {entry['op']}"
        print(f"    [{i}] {status}")
        if entry["c"]:
            print(f"        canonical : {entry['c']}")
        if entry["m"].get("reason"):
            print(f"        reason    : {entry['m']['reason']}")
        if entry["m"].get("field"):
            print(
                f"        field     : {entry['m']['field']}"
                f" ({entry['m'].get('invariant', '')})"
            )


# ---------------------------------------------------------------------------
# Example 1: Task domain
# ---------------------------------------------------------------------------

def run_task_example() -> None:
    _divider("Example 1: Task Domain (minimal)")

    raw = """
Task: Write the introduction
Priority: high
"""
    _step("Raw model output", raw.strip())

    with open("sl_spec.yaml", "r") as f:
        task_schema = yaml.safe_load(f)

    compiler = RELCompiler(task_schema, model_version="demo-1.0")
    try:
        lowered, warnings = compiler.compile_with_warnings(raw)
    except RELFailure as e:
        print(f"\n  REL extraction failed: {e}")
        return

    _step("REL output (lowered)", _strip_provenance(lowered))
    if warnings:
        _step("REL warnings", warnings)

    sol = TaskSOL.from_dict(lowered)
    _step("SOL object", sol.as_dict())
    _step("Canonical form (object level)", sol.canonical())

    trace = ConstitutionalTrace(task_schema)
    result = collapse(sol.as_dict(), task_schema, trace)
    _step("Collapse result", result)
    _print_trace(trace)


# ---------------------------------------------------------------------------
# Example 2a: Credit domain — clean object
# ---------------------------------------------------------------------------

def run_credit_clean() -> None:
    _divider("Example 2a: Credit Domain — clean object")

    raw = """
income: 42.0
credit_score: 0.31
"""
    _step("Raw model output", raw.strip())

    with open("credit_sl_spec.yaml", "r") as f:
        schema = yaml.safe_load(f)

    compiler = RELCompiler(schema, model_version="credit-model-1.0")
    try:
        lowered, warnings = compiler.compile_with_warnings(raw)
    except RELFailure as e:
        print(f"\n  REL extraction failed: {e}")
        return

    _step("REL output (lowered)", _strip_provenance(lowered))

    sol = CreditSOL.from_dict(lowered)
    _step("SOL object (full)", sol.as_dict())
    _step("Canonical form (object level)", sol.canonical())

    invariant_report = sol.check_invariants()
    print("\n  Invariant check:")
    for inv_id, satisfied, reason in invariant_report:
        mark = "✓" if satisfied else "✗"
        print(f"    {mark} {inv_id}" + (f": {reason}" if reason else ""))

    trace = ConstitutionalTrace(schema)
    result = collapse(sol.as_dict(), schema, trace)
    _step("Collapse result", result)
    _print_trace(trace)


# ---------------------------------------------------------------------------
# Example 2b: Credit domain — proxy and drift fields present
# ---------------------------------------------------------------------------

def run_credit_with_unsafe_fields() -> None:
    _divider("Example 2b: Credit Domain — proxy + drift fields present")

    raw = """
income: 42.0
zip_code: 10453
latent_cluster: 7
credit_score: 0.31
"""
    _step("Raw model output", raw.strip())

    with open("credit_sl_spec.yaml", "r") as f:
        schema = yaml.safe_load(f)

    compiler = RELCompiler(schema, model_version="credit-model-1.0")
    try:
        lowered, warnings = compiler.compile_with_warnings(raw)
    except RELFailure as e:
        print(f"\n  REL extraction failed: {e}")
        return

    _step("REL output (lowered)", _strip_provenance(lowered))

    sol = CreditSOL.from_dict(lowered)
    _step("SOL object (full, pre-pipeline)", sol.as_dict())

    invariant_report = sol.check_invariants()
    print("\n  Invariant check (pre-pipeline):")
    for inv_id, satisfied, reason in invariant_report:
        mark = "✓" if satisfied else "✗"
        print(f"    {mark} {inv_id}" + (f": {reason}" if reason else ""))

    print("\n  Running canonical pipeline (Norm → ε → Sanitize → Canon → Collapse)...")
    trace = ConstitutionalTrace(schema)
    result = collapse(sol.as_dict(), schema, trace)

    if result is not None:
        _step("Canonical form (post-pipeline)", result)
        print("\n  Fields pruned by Sanitize:")
        pruned = set(sol.as_dict().keys()) - set(result.keys())
        for field in sorted(pruned):
            print(f"    - {field}")
    else:
        _step("Collapse result", "⊥ — no invariant-satisfying form exists")

    _print_trace(trace)


# ---------------------------------------------------------------------------
# Example 2c: Credit domain — object that produces ⊥
# ---------------------------------------------------------------------------

def run_credit_bottom() -> None:
    _divider("Example 2c: Credit Domain — object producing ⊥")

    raw = """
income: -5.0
credit_score: 0.31
"""
    _step("Raw model output", raw.strip())

    with open("credit_sl_spec.yaml", "r") as f:
        schema = yaml.safe_load(f)

    compiler = RELCompiler(schema, model_version="credit-model-1.0")
    try:
        lowered, warnings = compiler.compile_with_warnings(raw)
    except RELFailure as e:
        print(f"\n  REL extraction failed: {e}")
        return

    _step("REL output (lowered)", _strip_provenance(lowered))

    sol = CreditSOL.from_dict(lowered)
    _step("SOL object", sol.as_dict())
    _step("is_well_formed()", sol.is_well_formed())

    print("\n  Running canonical pipeline...")
    trace = ConstitutionalTrace(schema)
    result = collapse(sol.as_dict(), schema, trace)
    _step("Collapse result", result if result is not None else "⊥")

    print("\n  This object cannot be committed. The failure is recorded")
    print("  in the constitutional trace as a first-class event,")
    print("  not silently dropped.")
    _print_trace(trace)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_task_example()
    run_credit_clean()
    run_credit_with_unsafe_fields()
    run_credit_bottom()

    print(f"\n{'=' * 64}")
    print("  All examples complete.")
    print(f"{'=' * 64}\n")
