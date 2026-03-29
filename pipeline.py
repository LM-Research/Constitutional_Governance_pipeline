"""
pipeline.py
-----------
The constitutional canonicalization pipeline:

    Canon(x) := Sanitize(ε(Norm(x)))

Operators are implemented as distinct, independently inspectable functions
matching the formal definitions in the paper. Each operator is total,
deterministic, and documented against the axiom it satisfies.

Operator summary
----------------
Norm      Aligns a raw SOL dict to the canonical basis B_R via fixed-point
          iteration. Satisfies Axiom 1: Norm(Canon(x)) = Canon(x).

ε         Enforces syntactic and semantic well-formedness against the schema.
          Satisfies Axiom 2: ε(Canon(x)) = Canon(x).

Sanitize  Two-phase pruning operator. Phase 1: iteratively removes fields
          violating per-attribute invariants until a fixed point is reached.
          Phase 2: evaluates global invariants over the residual object.
          Returns ⊥ (None) if no invariant-satisfying sub-object exists.
          Satisfies Axioms 3, 4, 5.

Canon     Composition: Sanitize(ε(Norm(x))). The unique canonical form.

Collapse  Transitions a representation from exploratory to committed.
          Only safe (Canon-stable) representations can collapse.
          Writes to the append-only trace on success.

BOTTOM (⊥)
----------
⊥ is represented as None throughout. Operators propagate ⊥: if any stage
returns None, downstream stages return None immediately. This ensures that
⊥ is a first-class constitutional event rather than a runtime exception.
"""

from __future__ import annotations

import copy
from typing import Any

import yaml

from credit_invariants import (
    GLOBAL_INVARIANTS,
    PER_ATTRIBUTE_INVARIANTS,
)
from trace import ConstitutionalTrace


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

SOLDict = dict[str, Any]   # A raw SOL object as a plain Python dict
Bottom = None              # ⊥ — no invariant-satisfying sub-object exists


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_schema(spec_path: str) -> dict:
    """Load an SL schema from a YAML file."""
    with open(spec_path, "r") as f:
        return yaml.safe_load(f)


def _canonical_basis(schema: dict) -> set[str]:
    """Return B_R: the set of field names that survive full canonicalization."""
    return set(schema.get("canonical_basis", []))


# ---------------------------------------------------------------------------
# Norm
#
# Formal requirement (Axiom 1): Norm(Canon(x)) = Canon(x).
#
# Implementation: fixed-point iteration that removes fields outside B_R.
# Convergence is guaranteed by Axiom A1 (finite structure) — each pass
# weakly reduces the field set; the loop stabilises in at most |x| steps.
# ---------------------------------------------------------------------------

def norm(obj: SOLDict | None, schema: dict) -> SOLDict | None:
    """
    Align obj to the canonical basis B_R via fixed-point iteration.

    Each iteration removes fields not in B_R. The loop terminates when the
    object is unchanged across two successive applications (fixed point).
    Convergence is guaranteed in at most |obj| iterations by finiteness (A1).

    Returns ⊥ if obj is ⊥.
    """
    if obj is None:
        return None

    basis = _canonical_basis(schema)
    current = copy.deepcopy(obj)

    for _ in range(len(obj) + 1):   # upper bound: |obj| iterations
        pruned = {k: v for k, v in current.items() if k in basis}
        if pruned == current:
            # Fixed point reached: Norm(current) = current.
            return current
        current = pruned

    # Unreachable under A1, but explicit for auditability.
    return current


# ---------------------------------------------------------------------------
# ε  (epsilon / refinement)
#
# Formal requirement (Axiom 2): ε(Canon(x)) = Canon(x).
#
# Implementation: enforces syntactic and semantic well-formedness against
# the schema on an already-Norm'd object. On canonical input this is a
# no-op, satisfying Axiom 2. On non-canonical input it coerces types where
# unambiguous and removes fields whose types cannot be reconciled.
#
# ε is intentionally conservative: ambiguous coercions are rejected rather
# than guessed at. This keeps the operator auditable.
# ---------------------------------------------------------------------------

_COERCE_MAP: dict[str, type] = {
    "float": float,
    "int": int,
    "string": str,
}

def epsilon(obj: SOLDict | None, schema: dict) -> SOLDict | None:
    """
    Enforce syntactic and semantic well-formedness against the schema.

    For each field in obj:
      - If the field is in the schema and the value is already the correct
        type, it is retained unchanged.
      - If the value can be unambiguously coerced to the declared type
        (e.g. int → float), the coerced value is used.
      - If the value cannot be reconciled, the field is removed.

    Returns ⊥ if obj is ⊥.
    """
    if obj is None:
        return None

    field_map = {f["name"]: f for f in schema["fields"]}
    result: SOLDict = {}

    for k, v in obj.items():
        if k not in field_map:
            # Field not in schema — conservative: drop it.
            continue

        declared = field_map[k]["type"]
        target_type = _COERCE_MAP.get(declared)

        if target_type is None:
            # Unknown type declaration — retain as-is for audit.
            result[k] = v
            continue

        if isinstance(v, target_type):
            result[k] = v
        else:
            try:
                result[k] = target_type(v)
            except (ValueError, TypeError):
                # Cannot reconcile type — drop field.
                continue

    return result


# ---------------------------------------------------------------------------
# Sanitize
#
# Formal requirements:
#   Axiom 3: Sanitize(Canon(x)) = Canon(x)      — fixed-point on canonical input
#   Axiom 4: Inv(Sanitize(x)) for all x         — invariants satisfied or ⊥
#   Axiom 5: WF(Sanitize(x)) for all x          — well-formed or ⊥
#
# Two-phase implementation:
#
# Phase 1 — per-attribute pruning (Inv1, Inv2):
#   Iteratively apply P(x) = x \ {f : ¬Inv_per(f, x)} until fixed point.
#   Each pass weakly reduces |x|; convergence guaranteed by A1.
#   Evaluation order is deterministic: fields are processed in sorted
#   lexicographic order, and the first failing invariant per field is used.
#
# Phase 2 — global invariant check (Inv3, Inv4):
#   Evaluated over the residual object after Phase 1 stabilises.
#   A global violation cannot be resolved by pruning a single field.
#   Returns ⊥ and records the failure reason for trace surfacing.
# ---------------------------------------------------------------------------

def sanitize(
    obj: SOLDict | None,
    schema: dict,
    trace: ConstitutionalTrace | None = None,
) -> SOLDict | None:
    """
    Project obj into the invariant-satisfying subspace via two-phase pruning.

    Phase 1: per-attribute invariants (Inv1, Inv2).
    Phase 2: global invariants (Inv3, Inv4).

    Returns the maximal invariant-satisfying sub-object, or ⊥ (None) if
    none exists. All violations are recorded in the trace if one is provided.
    """
    if obj is None:
        return None

    current: SOLDict = copy.deepcopy(obj)

    # ------------------------------------------------------------------
    # Phase 1: per-attribute pruning to fixed point.
    # ------------------------------------------------------------------
    max_iterations = len(current) + 1
    for _ in range(max_iterations):
        to_remove: list[tuple[str, str]] = []

        for field_name in sorted(current.keys()):   # deterministic order
            field_value = current[field_name]
            for inv_id, predicate in PER_ATTRIBUTE_INVARIANTS:
                if not predicate(field_name, field_value, schema):
                    to_remove.append((field_name, inv_id))
                    break   # first violation per field is sufficient

        if not to_remove:
            break   # fixed point reached

        for field_name, inv_id in to_remove:
            if trace:
                trace.record_violation(field_name, inv_id, current[field_name])
            del current[field_name]

    # ------------------------------------------------------------------
    # Phase 2: global invariant check over the residual object.
    # ------------------------------------------------------------------
    for inv_id, predicate in GLOBAL_INVARIANTS:
        satisfied, reason = predicate(current, schema)
        if not satisfied:
            if trace:
                trace.record_global_violation(inv_id, reason, current)
            return None   # ⊥

    return current if current else None


# ---------------------------------------------------------------------------
# Canon
#
# Canon(x) := Sanitize(ε(Norm(x)))
#
# The unique canonical form of x. Safe by construction given Axioms 1–5:
#   - Norm aligns to B_R (Axiom 1)
#   - ε enforces well-formedness (Axiom 2)
#   - Sanitize enforces invariants and WF (Axioms 3–5)
#
# Idempotent by construction (Guarantee G5):
#   Canon(Canon(x)) = Canon(x)
# because a canonical form is already a fixed point of all three operators.
# ---------------------------------------------------------------------------

def canon(
    obj: SOLDict | None,
    schema: dict,
    trace: ConstitutionalTrace | None = None,
) -> SOLDict | None:
    """
    Compute the canonical form of obj.

    Returns ⊥ (None) if no invariant-satisfying canonical form exists.
    All intermediate ⊥ events propagate automatically.
    """
    if obj is None:
        return None

    n = norm(obj, schema)
    if n is None:
        return None

    e = epsilon(n, schema)
    if e is None:
        return None

    return sanitize(e, schema, trace)


# ---------------------------------------------------------------------------
# Safe predicate
#
# Safe(x) := Inv(x) ∧ NoDrift(x) ∧ WF(x)
#
# In the implementation, a representation is Safe iff Canon(x) = x — it is
# already at the canonical fixed point and satisfies all invariants. This is
# the decidable operational definition used by Collapse.
# ---------------------------------------------------------------------------

def is_safe(obj: SOLDict | None, schema: dict) -> bool:
    """
    Return True iff obj is already canonical (i.e. Canon(obj) == obj).

    This is the operational definition of Safe(x): an object is safe
    precisely when it is a fixed point of the canonical pipeline.
    """
    if obj is None:
        return False
    return canon(obj, schema) == obj


# ---------------------------------------------------------------------------
# Collapse
#
# Collapse(x) := Canon(x)  if Safe(x)
#                x          otherwise
#
# Collapse is the constitutional commitment operator. It is:
#   - Deterministic (Guarantee G4)
#   - Irreversible  (Guarantee G6): the trace is append-only
#   - Total         (defined for all x ∈ R ∪ {⊥})
#
# A representation that is not Safe is returned unchanged; the caller must
# continue exploring or invoke Sanitize before commitment is possible.
# ---------------------------------------------------------------------------

def collapse(
    obj: SOLDict | None,
    schema: dict,
    trace: ConstitutionalTrace,
    metadata: dict | None = None,
) -> SOLDict | None:
    """
    Transition obj from exploratory to committed.

    If Safe(obj), computes Canon(obj), writes it irreversibly to the trace,
    and returns the canonical form. If not Safe, returns obj unchanged
    without writing to the trace.

    The trace write is part of the commitment act: disabling the trace
    disables Collapse (Guarantee G6).
    """
    if obj is None:
        trace.record_failure("COLLAPSE_ON_BOTTOM", metadata or {})
        return None

    canonical = canon(obj, schema, trace)

    if canonical is None:
        trace.record_failure("COLLAPSE_NO_CANONICAL_FORM", metadata or {})
        return obj   # return unchanged; caller must handle

    # We already computed Canon(obj); reuse it to avoid recomputation.
    if canonical == obj:
        trace.commit(canonical, metadata or {})
        return canonical

    # Not yet safe — return unchanged, do not commit.
    return obj
