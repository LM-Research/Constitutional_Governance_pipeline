"""
test_axioms.py
--------------
Property-based verification of Axioms 1–5 and Guarantees 3–7 for the
constitutional canonicalization pipeline.

The tests operate at two levels:

- SOLDict level: exercising the canonical pipeline
  (Norm, ε, Sanitize, Canon, Collapse, is_safe)
- SOL level: exercising CreditSOL / TaskSOL behaviour and invariants

Hypothesis is used to generate a wide range of credit-domain objects,
including ones that violate invariants. The axioms and guarantees are
required to hold over all x ∈ R, not just safe objects.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from credit_invariants import GLOBAL_INVARIANTS, PER_ATTRIBUTE_INVARIANTS
from pipeline import canon, collapse, epsilon, is_safe, norm, sanitize
from sol import CreditSOL, TaskSOL
from trace import ConstitutionalTrace


# ---------------------------------------------------------------------------
# Shared schema and helpers
# ---------------------------------------------------------------------------

with open("credit_sl_spec.yaml", "r") as _f:
    SCHEMA: dict[str, Any] = yaml.safe_load(_f)


def fresh_trace() -> ConstitutionalTrace:
    """Return a new, empty constitutional trace for the credit schema."""
    return ConstitutionalTrace(SCHEMA)


def is_bottom(x: Any) -> bool:
    """⊥ is represented as None throughout the pipeline."""
    return x is None


# ---------------------------------------------------------------------------
# Hypothesis strategies for credit-domain SOLDicts
# ---------------------------------------------------------------------------

class Strategies:
    """
    Strategies for generating credit-domain dicts (SOLDict-level).

    The pipeline operates on plain dicts, so all axiom and guarantee tests
    are expressed at the dict level. SOL-level tests appear separately.
    """

    # Positive income values (including a boundary just above zero).
    income = st.one_of(
        st.floats(
            min_value=0.001,
            max_value=1_000.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        st.just(0.001),
    )

    # Income values that violate Inv3 (zero or negative).
    income_invalid = st.one_of(
        st.just(0.0),
        st.floats(
            min_value=-1_000.0,
            max_value=-0.001,
            allow_nan=False,
            allow_infinity=False,
        ),
    )

    # Credit scores in [0, 1] — valid for Inv3.
    credit_score_valid = st.floats(
        min_value=0.0,
        max_value=1.0,
        allow_nan=False,
        allow_infinity=False,
    )

    # Credit scores outside [0, 1] — should lead to ⊥ after Sanitize.
    credit_score_invalid = st.one_of(
        st.floats(
            min_value=1.001,
            max_value=100.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        st.floats(
            min_value=-100.0,
            max_value=-0.001,
            allow_nan=False,
            allow_infinity=False,
        ),
    )

    # Optional non-canonical fields.
    zip_code = st.one_of(st.none(), st.from_regex(r"\d{5}", fullmatch=True))
    latent_cluster = st.one_of(
        st.none(), st.integers(min_value=0, max_value=99)
    )

    @classmethod
    def valid_credit_dict(cls) -> st.SearchStrategy[dict]:
        """Dicts that should survive canonicalization (income + valid score)."""
        return st.fixed_dictionaries(
            {
                "income": cls.income,
                "credit_score": cls.credit_score_valid,
            }
        )

    @classmethod
    def full_credit_dict(cls) -> st.SearchStrategy[dict]:
        """
        Dicts with all four fields, including proxy and drift fields.

        These are safe to pass to canon(); Sanitize is expected to prune
        zip_code and latent_cluster when present.
        """
        return (
            st.fixed_dictionaries(
                {
                    "income": cls.income,
                    "credit_score": cls.credit_score_valid,
                    "zip_code": cls.zip_code,
                    "latent_cluster": cls.latent_cluster,
                }
            )
            .map(lambda d: {k: v for k, v in d.items() if v is not None})
        )

    @classmethod
    def any_credit_dict(cls) -> st.SearchStrategy[dict]:
        """
        Dicts over the full credit schema, including invariant-violating ones.

        Used for axioms that must hold over all x ∈ R, not just safe objects.
        """
        return (
            st.fixed_dictionaries(
                {
                    "income": st.one_of(cls.income, cls.income_invalid),
                    "credit_score": st.one_of(
                        cls.credit_score_valid, cls.credit_score_invalid
                    ),
                    "zip_code": cls.zip_code,
                    "latent_cluster": cls.latent_cluster,
                }
            )
            .map(lambda d: {k: v for k, v in d.items() if v is not None})
        )


# ---------------------------------------------------------------------------
# Axiom 1 — Norm fixed point: Norm(Canon(x)) = Canon(x)
# ---------------------------------------------------------------------------

class TestAxiom1NormFixedPoint:
    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_norm_fixed_point_on_canonical(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return

        normed = norm(canonical, SCHEMA)
        assert normed == canonical, (
            "Axiom 1 violated: Norm(Canon(x)) != Canon(x)\n"
            f"  Canon(x)       = {canonical}\n"
            f"  Norm(Canon(x)) = {normed}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_norm_fixed_point_over_full_space(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return
        assert norm(canonical, SCHEMA) == canonical


# ---------------------------------------------------------------------------
# Axiom 2 — Refinement fixed point: ε(Canon(x)) = Canon(x)
# ---------------------------------------------------------------------------

class TestAxiom2RefinementFixedPoint:
    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_epsilon_fixed_point_on_canonical(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return

        eps = epsilon(canonical, SCHEMA)
        assert eps is not None
        stripped = {k: v for k, v in eps.items() if not k.startswith("_")}
        assert stripped == canonical, (
            "Axiom 2 violated: ε(Canon(x)) != Canon(x)\n"
            f"  Canon(x)    = {canonical}\n"
            f"  ε(Canon(x)) = {stripped}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_epsilon_fixed_point_over_full_space(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return
        eps = epsilon(canonical, SCHEMA)
        stripped = {k: v for k, v in eps.items() if not k.startswith("_")}
        assert stripped == canonical


# ---------------------------------------------------------------------------
# Axiom 3 — Sanitize fixed point: Sanitize(Canon(x)) = Canon(x)
# ---------------------------------------------------------------------------

class TestAxiom3SanitizeFixedPoint:
    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_sanitize_fixed_point_on_canonical(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return

        sanitized = sanitize(canonical, SCHEMA)
        assert sanitized == canonical, (
            "Axiom 3 violated: Sanitize(Canon(x)) != Canon(x)\n"
            f"  Canon(x)           = {canonical}\n"
            f"  Sanitize(Canon(x)) = {sanitized}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_sanitize_fixed_point_over_full_space(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return
        assert sanitize(canonical, SCHEMA) == canonical


# ---------------------------------------------------------------------------
# Axiom 4 — Sanitize restores invariants: Inv(Sanitize(x))
# ---------------------------------------------------------------------------

class TestAxiom4SanitizeRestoresInvariants:
    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_per_attribute_invariants_hold_after_sanitize(self, obj: dict) -> None:
        result = sanitize(obj, SCHEMA)
        if is_bottom(result):
            return

        for field_name, field_value in result.items():
            for inv_id, predicate in PER_ATTRIBUTE_INVARIANTS:
                assert predicate(field_name, field_value, SCHEMA), (
                    f"Axiom 4 violated: {inv_id} fails on '{field_name}' "
                    "after Sanitize\n"
                    f"  input  = {obj}\n"
                    f"  output = {result}"
                )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_global_invariants_hold_after_sanitize(self, obj: dict) -> None:
        result = sanitize(obj, SCHEMA)
        if is_bottom(result):
            return

        for inv_id, predicate in GLOBAL_INVARIANTS:
            ok, reason = predicate(result, SCHEMA)
            assert ok, (
                f"Axiom 4 violated: {inv_id} fails after Sanitize\n"
                f"  reason = {reason}\n"
                f"  input  = {obj}\n"
                f"  output = {result}"
            )


# ---------------------------------------------------------------------------
# Axiom 5 — Sanitize enforces well-formedness: WF(Sanitize(x))
# ---------------------------------------------------------------------------

class TestAxiom5SanitizeEnforcesWellFormedness:
    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_sanitize_output_is_well_formed(self, obj: dict) -> None:
        result = sanitize(obj, SCHEMA)
        if is_bottom(result):
            return

        required = {
            f["name"]
            for f in SCHEMA["fields"]
            if f.get("required", False)
        }
        for name in required:
            assert name in result, (
                "Axiom 5 violated: required field missing after Sanitize\n"
                f"  field  = {name}\n"
                f"  input  = {obj}\n"
                f"  output = {result}"
            )


# ---------------------------------------------------------------------------
# Guarantee 3 — Pipeline safety: Safe(Canon(x))
# ---------------------------------------------------------------------------

class TestGuarantee3PipelineSafety:
    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_canonical_output_is_safe(self, obj: dict) -> None:
        canonical = canon(obj, SCHEMA)
        if is_bottom(canonical):
            return

        assert is_safe(canonical, SCHEMA), (
            "Guarantee 3 violated: Canon(x) is not safe\n"
            f"  input    = {obj}\n"
            f"  Canon(x) = {canonical}"
        )


# ---------------------------------------------------------------------------
# Guarantee 4 — Deterministic collapse
# ---------------------------------------------------------------------------

class TestGuarantee4DeterministicCollapse:
    @given(Strategies.full_credit_dict(), Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_same_canonical_same_collapse(
        self, obj_a: dict, obj_b: dict
    ) -> None:
        trace_a = fresh_trace()
        trace_b = fresh_trace()

        canon_a = canon(obj_a, SCHEMA)
        canon_b = canon(obj_b, SCHEMA)

        if is_bottom(canon_a) or is_bottom(canon_b):
            return
        if canon_a != canon_b:
            return

        result_a = collapse(obj_a, SCHEMA, trace_a)
        result_b = collapse(obj_b, SCHEMA, trace_b)

        assert result_a == result_b, (
            "Guarantee 4 violated: same Canon(x) but different Collapse(x)\n"
            f"  Canon(x)   = {canon_a}\n"
            f"  Collapse(a) = {result_a}\n"
            f"  Collapse(b) = {result_b}"
        )

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_collapse_is_deterministic_on_repeated_calls(
        self, obj: dict
    ) -> None:
        trace_1 = fresh_trace()
        trace_2 = fresh_trace()

        result_1 = collapse(obj, SCHEMA, trace_1)
        result_2 = collapse(obj, SCHEMA, trace_2)

        assert result_1 == result_2, (
            "Guarantee 4 violated: Collapse(x) is non-deterministic\n"
            f"  input    = {obj}\n"
            f"  result_1 = {result_1}\n"
            f"  result_2 = {result_2}"
        )


# ---------------------------------------------------------------------------
# Guarantee 5 — Canonical idempotence: Canon(Canon(x)) = Canon(x)
# ---------------------------------------------------------------------------

class TestGuarantee5CanonicalIdempotence:
    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_canon_is_idempotent(self, obj: dict) -> None:
        first = canon(obj, SCHEMA)
        if is_bottom(first):
            # ⊥ is a fixed point: Canon(⊥) = ⊥.
            assert is_bottom(canon(None, SCHEMA))
            return

        second = canon(first, SCHEMA)
        assert second == first, (
            "Guarantee 5 violated: Canon is not idempotent\n"
            f"  input           = {obj}\n"
            f"  Canon(x)        = {first}\n"
            f"  Canon(Canon(x)) = {second}"
        )


# ---------------------------------------------------------------------------
# Guarantee 6 — Irreversibility of collapse (append-only trace)
# ---------------------------------------------------------------------------

class TestGuarantee6IrreversibilityOfCollapse:
    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_trace_entries_are_immutable_after_commit(self, obj: dict) -> None:
        trace = fresh_trace()
        collapse(obj, SCHEMA, trace)

        if len(trace) == 0:
            return  # no commit occurred; vacuous

        first_entry = trace[0]
        snapshot = copy.deepcopy(first_entry)

        # Further operations must not mutate existing entries.
        collapse(obj, SCHEMA, trace)
        canon(obj, SCHEMA)

        assert trace[0] == snapshot, (
            "Guarantee 6 violated: trace entry mutated after commit\n"
            f"  original = {snapshot}\n"
            f"  current  = {trace[0]}"
        )

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_trace_length_is_monotone(self, obj: dict) -> None:
        trace = fresh_trace()
        lengths: list[int] = []

        for _ in range(3):
            collapse(obj, SCHEMA, trace)
            lengths.append(len(trace))

        assert lengths == sorted(lengths), (
            "Guarantee 6 violated: trace length decreased\n"
            f"  lengths = {lengths}"
        )


# ---------------------------------------------------------------------------
# Guarantee 7 — Canonical trace invariant (all commits are safe)
# ---------------------------------------------------------------------------

class TestGuarantee7CanonicalTraceInvariant:
    @given(st.lists(Strategies.any_credit_dict(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_all_commits_are_safe(self, objects: list[dict]) -> None:
        trace = fresh_trace()

        for obj in objects:
            collapse(obj, SCHEMA, trace)

        for entry in trace.commits():
            assert entry.c is not None, (
                "Guarantee 7 violated: COMMIT entry without canonical form"
            )
            assert is_safe(entry.c, SCHEMA), (
                "Guarantee 7 violated: unsafe canonical form in COMMIT entry\n"
                f"  entry.c = {entry.c}"
            )

    @given(st.lists(Strategies.any_credit_dict(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_no_unsafe_canonical_state_in_trace(
        self, objects: list[dict]
    ) -> None:
        trace = fresh_trace()

        for obj in objects:
            collapse(obj, SCHEMA, trace)

        for entry in trace:
            if entry.c is not None:
                assert is_safe(entry.c, SCHEMA), (
                    "Guarantee 7 violated: unsafe canonical state in trace\n"
                    f"  entry = {entry}"
                )


# ---------------------------------------------------------------------------
# SOL-level tests — CreditSOL and TaskSOL behaviour
# ---------------------------------------------------------------------------

class TestCreditSOLInvariants:
    def test_clean_credit_object_passes_all_invariants(self) -> None:
        obj = CreditSOL(income=42.0, credit_score=0.31)
        results = obj.check_invariants()
        for inv_id, ok, reason in results:
            assert ok, f"{inv_id} failed unexpectedly: {reason}"

    def test_proxy_field_triggers_inv1(self) -> None:
        obj = CreditSOL(income=42.0, credit_score=0.31, zip_code="10453")
        results = {
            inv_id: (ok, reason)
            for inv_id, ok, reason in obj.check_invariants()
        }
        assert not results["Inv1"][0], "Inv1 should fail when zip_code present"

    def test_drift_field_triggers_inv2(self) -> None:
        obj = CreditSOL(income=42.0, credit_score=0.31, latent_cluster=7)
        results = {
            inv_id: (ok, reason)
            for inv_id, ok, reason in obj.check_invariants()
        }
        assert not results["Inv2"][0], (
            "Inv2 should fail when latent_cluster present"
        )

    def test_invalid_score_triggers_inv3(self) -> None:
        obj = CreditSOL(income=42.0, credit_score=1.5)
        results = {
            inv_id: (ok, reason)
            for inv_id, ok, reason in obj.check_invariants()
        }
        assert not results["Inv3"][0], "Inv3 should fail for score > 1"

    def test_negative_income_triggers_inv3(self) -> None:
        obj = CreditSOL(income=-1.0, credit_score=0.5)
        results = {
            inv_id: (ok, reason)
            for inv_id, ok, reason in obj.check_invariants()
        }
        assert not results["Inv3"][0], "Inv3 should fail for non-positive income"

    def test_equivalence_relation_on_canonical_projection(self) -> None:
        a = CreditSOL(income=42.0, credit_score=0.31, zip_code="10453")
        b = CreditSOL(income=42.0, credit_score=0.31)
        assert a == b

    def test_different_canonical_forms_are_not_equal(self) -> None:
        a = CreditSOL(income=42.0, credit_score=0.31)
        b = CreditSOL(income=55.0, credit_score=0.45)
        assert a != b


class TestTaskSOLBehaviour:
    def test_task_sol_well_formed_and_canonical(self) -> None:
        obj = TaskSOL(task="Write introduction", priority="high")
        assert obj.is_well_formed()
        assert obj.canonical() == obj.as_dict()

    def test_task_sol_invalid_priority(self) -> None:
        with pytest.raises(ValueError):
            TaskSOL(task="Do something", priority="urgent")


# ---------------------------------------------------------------------------
# ⊥ propagation — all operators must propagate None cleanly
# ---------------------------------------------------------------------------

class TestBottomPropagation:
    def test_norm_propagates_bottom(self) -> None:
        assert norm(None, SCHEMA) is None

    def test_epsilon_propagates_bottom(self) -> None:
        assert epsilon(None, SCHEMA) is None

    def test_sanitize_propagates_bottom(self) -> None:
        assert sanitize(None, SCHEMA) is None

    def test_canon_propagates_bottom(self) -> None:
        assert canon(None, SCHEMA) is None

    def test_is_safe_false_on_bottom(self) -> None:
        assert not is_safe(None, SCHEMA)

    def test_collapse_records_failure_on_bottom(self) -> None:
        trace = fresh_trace()
        result = collapse(None, SCHEMA, trace)
        assert result is None
        failures = trace.failures()
        assert len(failures) == 1
        assert failures[0].op == "COLLAPSE_ON_BOTTOM"
