"""
credit_invariants.py
--------------------
Executable predicates for the credit‑scoring constitutional invariant set.

Corresponds to Table 1 in the paper:

    Inv1  ¬∃f ∈ Features(x) : Proxy(f)         Fairness      per‑attribute
    Inv2  ¬∃f ∈ Features(x) : LatentDrift(f)   Robustness    per‑attribute
    Inv3  Monotonic(income → score)           Validity      global
    Inv4  WF(x)                               Structural    global

Architecture
------------
Per‑attribute invariants (Inv1, Inv2) are evaluated field‑by‑field during
Sanitize’s pruning loop. Any field for which a predicate returns False is
removed. Because each pass weakly reduces cardinality, the loop converges
in at most |x| steps (Axiom A1 guarantees finiteness).

Global invariants (Inv3, Inv4) are evaluated over the residual object after
per‑attribute pruning has stabilised. A global violation cannot be resolved
by removing a single field; Sanitize returns ⊥ in that case, and the failure
is surfaced as a constitutional trace event rather than silently dropped.

Decidability note on Inv3
-------------------------
Monotonic(income → score) is formally a property of the scoring *function*
across objects, not of any single object. Its per‑object decidable
instantiation — verified here — is necessarily weaker: we check that income
is a positive numeric and credit_score lies in [0, 1], which are necessary
(not sufficient) conditions for any monotone scoring function. Full
monotonicity requires either a multi‑object witness set or a functional
specification of the scorer, both of which are outside the scope of a
reference implementation. This limitation is documented explicitly so that
domain engineers extending this example are not misled about the guarantee.
"""

from typing import Any, Callable, Dict, Tuple


# ===========================================================================
# Per‑attribute invariant predicates
# ---------------------------------------------------------------------------
# Signature: (field_name: str, field_value: Any, sl_spec: dict) -> bool
#
# Return True  → field is SAFE, retain it.
# Return False → field violates this invariant, Sanitize will prune it.
#
# Predicates read flags from the SL spec rather than hard‑coding field names,
# so the invariant set adapts automatically when the schema evolves.
# ===========================================================================

def inv1_not_proxy(field_name: str, field_value: Any, sl_spec: dict) -> bool:
    """
    Inv1 (Fairness): field must not be a protected proxy attribute.
    Reads the `protected_proxy` flag from the SL schema.
    Unknown fields (not in schema) are treated as unsafe by default.
    """
    schema = {f["name"]: f for f in sl_spec["fields"]}
    if field_name not in schema:
        return False
    return not schema[field_name].get("protected_proxy", False)


def inv2_not_latent_drift(field_name: str, field_value: Any, sl_spec: dict) -> bool:
    """
    Inv2 (Robustness): field must not be a drift‑induced latent feature.
    Reads the `latent_drift` flag from the SL schema.
    Unknown fields are treated as unsafe by default.
    """
    schema = {f["name"]: f for f in sl_spec["fields"]}
    if field_name not in schema:
        return False
    return not schema[field_name].get("latent_drift", False)


# Ordered list applied during Sanitize’s pruning loop.
# Order matters: Inv1 is checked before Inv2, matching Table 1.
PER_ATTRIBUTE_INVARIANTS: list[tuple[str, Callable[..., bool]]] = [
    ("Inv1", inv1_not_proxy),
    ("Inv2", inv2_not_latent_drift),
]


# ===========================================================================
# Global invariant predicates
# ---------------------------------------------------------------------------
# Signature: (obj: dict, sl_spec: dict) -> tuple[bool, str]
#
# Return (True, "")            → invariant satisfied.
# Return (False, reason: str)  → invariant violated; Sanitize returns ⊥.
#
# Global invariants are evaluated after per‑attribute pruning stabilises.
# The first failure short‑circuits; the reason string is recorded in the
# constitutional trace event.
# ===========================================================================

def inv3_monotonic_income_score(obj: dict, sl_spec: dict) -> Tuple[bool, str]:
    """
    Inv3 (Validity): per‑object decidable instantiation of
    Monotonic(income → score). See module docstring for limitations.
    """
    if "income" not in obj:
        return False, "Inv3: 'income' absent from residual object"
    if "credit_score" not in obj:
        return False, "Inv3: 'credit_score' absent from residual object"

    income = obj["income"]
    score = obj["credit_score"]

    if not isinstance(income, (int, float)) or income <= 0:
        return False, f"Inv3: income must be positive numeric, got {income!r}"

    if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
        return False, f"Inv3: credit_score must be in [0, 1], got {score!r}"

    return True, ""


def inv4_well_formed(obj: dict, sl_spec: dict) -> Tuple[bool, str]:
    """
    Inv4 (Structural): object must be well‑formed with respect to the SL
    schema — all required fields present and all values correctly typed.
    """
    type_map: Dict[str, Any] = {
        "float": (int, float),
        "int": int,
        "string": str,
    }

    for field in sl_spec["fields"]:
        name = field["name"]

        # Required field missing
        if field.get("required", False) and name not in obj:
            return False, f"Inv4: required field '{name}' missing"

        # Type mismatch
        if name in obj:
            expected = type_map.get(field["type"])
            if expected and not isinstance(obj[name], expected):
                return (
                    False,
                    f"Inv4: '{name}' expected {field['type']}, "
                    f"got {type(obj[name]).__name__}",
                )

    return True, ""


# Ordered list evaluated after pruning stabilises.
GLOBAL_INVARIANTS: list[tuple[str, Callable[..., Tuple[bool, str]]]] = [
    ("Inv3", inv3_monotonic_income_score),
    ("Inv4", inv4_well_formed),
]
