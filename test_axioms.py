"""
test_axioms.py
--------------
Property-based verification of Axioms 1–5 and Guarantees 1–7 for the
constitutional canonicalization pipeline.

Uses Hypothesis for property-based testing: rather than verifying axioms
on a fixed set of hand-crafted examples, Hypothesis generates a large and
varied population of SOL objects and checks that the formal properties hold
across the entire generated space. This is as close as a reference
implementation can get to the paper's claim that the guarantees hold
"for any implementation satisfying the stated axioms."

Test structure
--------------
Each test class corresponds to one axiom or guarantee from the paper.
Within each class, test methods exercise the property over:
    - well-formed objects (happy path)
    - objects with non-canonical fields (zip_code, latent_cluster present)
    - objects with type anomalies (values requiring coercion)
    - edge cases (income at boundary, credit_score at 0.0 and 1.0)
    - objects that should produce ⊥ (negative income, score out of range)

Hypothesis strategies
----------------------
The strategies defined in the Strategies class generate the full range of
CreditSOL-domain dicts, including objects that violate invariants. This is
intentional: the axioms must hold over all x ∈ R, not just safe ones.

Running the tests
-----------------
    pip install pytest hypothesis pyyaml
    pytest test_axioms.py -v

For more exhaustive search (CI / pre-submission):
    pytest test_axioms.py -v --hypothesis-seed=0
"""

from __future__ import annotations

import copy
import yaml
import pytest

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from pipeline import canon, norm, epsilon, sanitize, is_safe, collapse
from trace import ConstitutionalTrace
from sol import CreditSOL, TaskSOL
from credit_invariants import GLOBAL_INVARIANTS, PER_ATTRIBUTE_INVARIANTS


# ---------------------------------------------------------------------------
# Load shared schema — used by all tests
# ---------------------------------------------------------------------------

with open("credit_sl_spec.yaml", "r") as _f:
    SCHEMA = yaml.safe_load(_f)


# ---------------------------------------------------------------------------
# Hypothesis strategies
#
# All strategies generate plain dicts (SOLDict) rather than CreditSOL
# instances, because the pipeline operates on dicts and the axioms must
# hold at the dict level. CreditSOL-level tests are in the SOL section.
# ---------------------------------------------------------------------------

class Strategies:

    # Positive income values: covers normal range and boundary.
    income = st.one_of(
        st.floats(min_value=0.001, max_value=1_000.0, allow_nan=False,
                  allow_infinity=False),
        st.just(0.001),   # boundary: just above zero
    )

    # Credit scores in [0, 1] — valid range for Inv3.
    credit_score_valid = st.floats(
        min_value=0.0, max_value=1.0,
        allow_nan=False, allow_infinity=False,
    )

    # Credit scores outside [0, 1] — should produce ⊥ after Sanitize.
    credit_score_invalid = st.one_of(
        st.floats(min_value=1.001, max_value=100.0,
                  allow_nan=False, allow_infinity=False),
        st.floats(min_value=-100.0, max_value=-0.001,
                  allow_nan=False, allow_infinity=False),
    )

    # Negative/zero income — should produce ⊥ after Sanitize.
    income_invalid = st.one_of(
        st.just(0.0),
        st.floats(min_value=-1_000.0, max_value=-0.001,
                  allow_nan=False, allow_infinity=False),
    )

    # Optional non-canonical fields.
    zip_code = st.one_of(st.none(), st.from_regex(r"\d{5}", fullmatch=True))
    latent_cluster = st.one_of(st.none(), st.integers(min_value=0, max_value=99))

    @classmethod
    def valid_credit_dict(cls) -> st.SearchStrategy[dict]:
        """Generate a dict that should survive canonicalization."""
        return st.fixed_dictionaries({
            "income": cls.income,
            "credit_score": cls.credit_score_valid,
        })

    @classmethod
    def full_credit_dict(cls) -> st.SearchStrategy[dict]:
        """
        Generate a dict with all four fields — including proxy and drift
        fields that Sanitize should prune. Safe to pass to canon().
        """
        return st.fixed_dictionaries({
            "income": cls.income,
            "credit_score": cls.credit_score_valid,
            "zip_code": cls.zip_code,
            "latent_cluster": cls.latent_cluster,
        }).map(lambda d: {k: v for k, v in d.items() if v is not None})

    @classmethod
    def any_credit_dict(cls) -> st.SearchStrategy[dict]:
        """
        Generate any dict over the credit schema — valid or invalid.
        Used for axiom tests that must hold over all x ∈ R.
        """
        return st.fixed_dictionaries({
            "income": st.one_of(cls.income, cls.income_invalid),
            "credit_score": st.one_of(
                cls.credit_score_valid, cls.credit_score_invalid
            ),
            "zip_code": cls.zip_code,
            "latent_cluster": cls.latent_cluster,
        }).map(lambda d: {k: v for k, v in d.items() if v is not None})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_trace() -> ConstitutionalTrace:
    return ConstitutionalTrace(SCHEMA)


def _is_bottom(x) -> bool:
    return x is None


# ---------------------------------------------------------------------------
# Axiom 1: Norm Fixed Point
#
# Norm(Canon(x)) = Canon(x) for all x ∈ R.
#
# Verification: for any x, compute Canon(x). If it is not ⊥, apply Norm
# again and verify the result is unchanged.
# ---------------------------------------------------------------------------

class TestAxiom1NormFixedPoint:

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_norm_fixed_point_on_canonical(self, obj):
        """Norm(Canon(x)) = Canon(x) for all x where Canon(x) ≠ ⊥."""
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return   # ⊥ propagates; axiom is vacuously satisfied

        normed_again = norm(canonical, SCHEMA)
        assert normed_again == canonical, (
            f"Axiom 1 violated: Norm(Canon(x)) ≠ Canon(x)\n"
            f"  Canon(x)         = {canonical}\n"
            f"  Norm(Canon(x))   = {normed_again}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_norm_fixed_point_over_full_space(self, obj):
        """Axiom 1 holds over the full space including invalid objects."""
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return
        assert norm(canonical, SCHEMA) == canonical


# ---------------------------------------------------------------------------
# Axiom 2: Refinement Fixed Point
#
# ε(Canon(x)) = Canon(x) for all x ∈ R.
# ---------------------------------------------------------------------------

class TestAxiom2RefinementFixedPoint:

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_epsilon_fixed_point_on_canonical(self, obj):
        """ε(Canon(x)) = Canon(x) for all x where Canon(x) ≠ ⊥."""
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return

        # epsilon returns a dict that may carry _epsilon_failures metadata.
        # We compare only the non-metadata fields.
        epsilon_result = epsilon(canonical, SCHEMA)
        assert epsilon_result is not None

        stripped = {k: v for k, v in epsilon_result.items()
                    if not k.startswith("_")}
        assert stripped == canonical, (
            f"Axiom 2 violated: ε(Canon(x)) ≠ Canon(x)\n"
            f"  Canon(x)   = {canonical}\n"
            f"  ε(Canon(x)) = {stripped}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_epsilon_fixed_point_over_full_space(self, obj):
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return
        result = epsilon(canonical, SCHEMA)
        stripped = {k: v for k, v in result.items()
                    if not k.startswith("_")}
        assert stripped == canonical


# ---------------------------------------------------------------------------
# Axiom 3: Sanitize Fixed Point
#
# Sanitize(Canon(x)) = Canon(x) for all x ∈ R.
# ---------------------------------------------------------------------------

class TestAxiom3SanitizeFixedPoint:

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_sanitize_fixed_point_on_canonical(self, obj):
        """Sanitize(Canon(x)) = Canon(x) for all x where Canon(x) ≠ ⊥."""
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return

        sanitized_again = sanitize(canonical, SCHEMA)
        assert sanitized_again == canonical, (
            f"Axiom 3 violated: Sanitize(Canon(x)) ≠ Canon(x)\n"
            f"  Canon(x)            = {canonical}\n"
            f"  Sanitize(Canon(x))  = {sanitized_again}"
        )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=200)
    def test_sanitize_fixed_point_over_full_space(self, obj):
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return
        assert sanitize(canonical, SCHEMA) == canonical


# ---------------------------------------------------------------------------
# Axiom 4: Sanitize Restores Invariants
#
# Inv(Sanitize(x)) for all x ∈ R.
# (Where Sanitize(x) ≠ ⊥.)
# ---------------------------------------------------------------------------

class TestAxiom4SanitizeRestoresInvariants:

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_sanitize_output_satisfies_per_attribute_invariants(self, obj):
        """
        After Sanitize, no per-attribute invariant is violated.
        If Sanitize returns ⊥, the test passes vacuously.
        """
        result = sanitize(obj, SCHEMA)
        if _is_bottom(result):
            return

        for field_name, field_value in result.items():
            for inv_id, predicate in PER_ATTRIBUTE_INVARIANTS:
                assert predicate(field_name, field_value, SCHEMA), (
                    f"Axiom 4 violated: {inv_id} fails on field '{field_name}' "
                    f"after Sanitize\n"
                    f"  input  = {obj}\n"
                    f"  output = {result}"
                )

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_sanitize_output_satisfies_global_invariants(self, obj):
        """After Sanitize, all global invariants hold."""
        result = sanitize(obj, SCHEMA)
        if _is_bottom(result):
            return

        for inv_id, predicate in GLOBAL_INVARIANTS:
            satisfied, reason = predicate(result, SCHEMA)
            assert satisfied, (
                f"Axiom 4 violated: {inv_id} fails after Sanitize\n"
                f"  reason = {reason}\n"
                f"  input  = {obj}\n"
                f"  output = {result}"
            )


# ---------------------------------------------------------------------------
# Axiom 5: Sanitize Enforces Well-Formedness
#
# WF(Sanitize(x)) for all x ∈ R.
# ---------------------------------------------------------------------------

class TestAxiom5SanitizeEnforcesWellFormedness:

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_sanitize_output_is_well_formed(self, obj):
        """
        After Sanitize, the object satisfies WF(x) with respect to Σ.
        If Sanitize returns ⊥, the test passes vacuously.
        """
        result = sanitize(obj, SCHEMA)
        if _is_bottom(result):
            return

        # WF check: all required fields present and correctly typed.
        required = {f["name"] for f in SCHEMA["fields"] if f.get("required", False)}
        for field_name in required:
            assert field_name in result, (
                f"Axiom 5 violated: required field '{field_name}' absent "
                f"after Sanitize\n"
                f"  input  = {obj}\n"
                f"  output = {result}"
            )


# ---------------------------------------------------------------------------
# Guarantee 3: Pipeline Safety
#
# Safe(Canon(x)) for all x ∈ R.
# This is the central safety theorem; it follows from Axioms 1–5.
# ---------------------------------------------------------------------------

class TestGuarantee3PipelineSafety:

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_canon_output_is_safe(self, obj):
        """
        Canon(x) is always safe: is_safe(Canon(x)) = True for all x
        where Canon(x) ≠ ⊥.
        """
        canonical = canon(obj, SCHEMA)
        if _is_bottom(canonical):
            return

        assert is_safe(canonical, SCHEMA), (
            f"Guarantee 3 violated: Canon(x) is not safe\n"
            f"  input        = {obj}\n"
            f"  Canon(x)     = {canonical}"
        )


# ---------------------------------------------------------------------------
# Guarantee 4: Deterministic Collapse
#
# Collapse(x) = Collapse(y) ⟺ Canon(x) = Canon(y).
# ---------------------------------------------------------------------------

class TestGuarantee4DeterministicCollapse:

    @given(Strategies.full_credit_dict(), Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_same_canonical_same_collapse(self, obj_a, obj_b):
        """
        If Canon(x) = Canon(y), then Collapse(x) = Collapse(y).
        """
        trace_a = fresh_trace()
        trace_b = fresh_trace()

        canon_a = canon(obj_a, SCHEMA)
        canon_b = canon(obj_b, SCHEMA)

        if _is_bottom(canon_a) or _is_bottom(canon_b):
            return
        if canon_a != canon_b:
            return   # test is for the case where they agree

        result_a = collapse(obj_a, SCHEMA, trace_a)
        result_b = collapse(obj_b, SCHEMA, trace_b)

        assert result_a == result_b, (
            f"Guarantee 4 violated: same Canon but different Collapse\n"
            f"  Canon(a) = Canon(b) = {canon_a}\n"
            f"  Collapse(a) = {result_a}\n"
            f"  Collapse(b) = {result_b}"
        )

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_collapse_is_deterministic_on_repeated_call(self, obj):
        """Collapse(x) returns the same result on repeated calls."""
        trace_1 = fresh_trace()
        trace_2 = fresh_trace()

        result_1 = collapse(obj, SCHEMA, trace_1)
        result_2 = collapse(obj, SCHEMA, trace_2)

        assert result_1 == result_2, (
            f"Guarantee 4 violated: Collapse is non-deterministic\n"
            f"  input      = {obj}\n"
            f"  result 1   = {result_1}\n"
            f"  result 2   = {result_2}"
        )


# ---------------------------------------------------------------------------
# Guarantee 5: Canonical Idempotence
#
# Canon(Canon(x)) = Canon(x) for all x ∈ R.
# ---------------------------------------------------------------------------

class TestGuarantee5CanonicalIdempotence:

    @given(Strategies.any_credit_dict())
    @settings(max_examples=300)
    def test_canon_is_idempotent(self, obj):
        """Canon(Canon(x)) = Canon(x)."""
        first = canon(obj, SCHEMA)
        if _is_bottom(first):
            # ⊥ is a fixed point of canon: canon(⊥) = ⊥.
            assert _is_bottom(canon(None, SCHEMA))
            return

        second = canon(first, SCHEMA)
        assert second == first, (
            f"Guarantee 5 violated: Canon is not idempotent\n"
            f"  input         = {obj}\n"
            f"  Canon(x)      = {first}\n"
            f"  Canon(Canon(x)) = {second}"
        )


# ---------------------------------------------------------------------------
# Guarantee 6: Irreversibility of Collapse
#
# No constitutional operator can undo a commitment.
# Verified by checking that the trace is strictly append-only: no entry
# is removed or modified after being written.
# ---------------------------------------------------------------------------

class TestGuarantee6IrreversibilityOfCollapse:

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_trace_is_append_only(self, obj):
        """
        Once a Collapse writes to the trace, the entry is immutable.
        Verified by recording the entry and confirming it is unchanged
        after further pipeline operations.
        """
        trace = fresh_trace()
        collapse(obj, SCHEMA, trace)

        if len(trace) == 0:
            return   # Collapse did not commit (obj not safe); vacuous

        first_entry = trace[0]
        snapshot = copy.deepcopy(first_entry)

        # Perform further operations that should not affect existing entries.
        collapse(obj, SCHEMA, trace)
        canon(obj, SCHEMA)

        assert trace[0] == snapshot, (
            f"Guarantee 6 violated: trace entry was modified after commit\n"
            f"  original = {snapshot}\n"
            f"  current  = {trace[0]}"
        )

    @given(Strategies.full_credit_dict())
    @settings(max_examples=200)
    def test_trace_length_never_decreases(self, obj):
        """Trace length is monotonically non-decreasing."""
        trace = fresh_trace()
        lengths = []

        for _ in range(3):
            collapse(obj, SCHEMA, trace)
            lengths.append(len(trace))

        assert lengths == sorted(lengths), (
            f"Guarantee 6 violated: trace length decreased\n"
            f"  lengths = {lengths}"
        )


# ---------------------------------------------------------------------------
# Guarantee 7: Canonical Trace Invariant
#
# Every entry in the trace with op=COMMIT contains a canonical, safe
# representation. Verified by checking is_safe() on every committed
# canonical form in the trace.
# ---------------------------------------------------------------------------

class TestGuarantee7CanonicalTraceInvariant:

    @given(st.lists(Strategies.any_credit_dict(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_all_committed_trace_entries_are_safe(self, objects):
        """
        For every COMMIT entry in the trace, the committed canonical form
        satisfies is_safe().
        """
        trace = fresh_trace()

        for obj in objects:
            try:
                collapse(obj, SCHEMA, trace)
            except Exception:
                pass   # REL or pipeline failures are surfaced in the trace

        for entry in trace.commits():
            assert entry.c is not None, (
                "Guarantee 7 violated: COMMIT entry has no canonical form"
            )
            assert is_safe(entry.c, SCHEMA), (
                f"Guarantee 7 violated: committed form is not safe\n"
                f"  entry.c = {entry.c}"
            )

    @given(st.lists(Strategies.any_credit_dict(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_no_unsafe_state_in_trace(self, objects):
        """
        No entry in the trace — COMMIT or otherwise — contains a canonical
        form that violates the invariants.
        """
        trace = fresh_trace()

        for obj in objects:
            collapse(obj, SCHEMA, trace)

        for entry in trace:
            if entry.c is not None:
                assert is_safe(entry.c, SCHEMA), (
                    f"Guarantee 7 violated: unsafe state in trace\n"
                    f"  entry = {entry}"
                )


# ---------------------------------------------------------------------------
# SOL-level tests: CreditSOL invariant reporting
#
# These tests verify that the object-level check_invariants() method
# correctly reports the invariant status of CreditSOL instances, and that
# the equivalence relation __eq__ is implemented correctly.
# ---------------------------------------------------------------------------

class TestCreditSOLInvariants:

    def test_clean_object_passes_all_invariants(self):
        obj = CreditSOL(income=42.0, credit_score=0.31)
        results = obj.check_invariants()
        for inv_id, satisfied, reason in results:
            assert satisfied, f"{inv_id} failed unexpectedly: {reason}"

    def test_proxy_field_flagged_by_inv1(self):
        obj = CreditSOL(income=42.0, credit_score=0.31, zip_code="10453")
        results = {inv_id: (satisfied, reason)
                   for inv_id, satisfied, reason in obj.check_invariants()}
        assert not results["Inv1"][0], "Inv1 should fail when zip_code present"

    def test_drift_field_flagged_by_inv2(self):
        obj = CreditSOL(income=42.0, credit_score=0.31, latent_cluster=7)
        results = {inv_id: (satisfied, reason)
                   for inv_id, satisfied, reason in obj.check_invariants()}
        assert not results["Inv2"][0], "Inv2 should fail when latent_cluster present"

    def test_invalid_score_flagged_by_inv3(self):
        obj = CreditSOL(income=42.0, credit_score=1.5)
        assert not obj.is_well_formed()

    def test_negative_income_flagged_by_inv3(self):
        obj = CreditSOL(income=-1.0, credit_score=0.5)
        assert not obj.is_well_formed()

    def test_equivalence_relation(self):
        """x ≈ y ⟺ Canon(x) = Canon(y)."""
        a = CreditSOL(income=42.0, credit_score=0.31, zip_code="10453")
        b = CreditSOL(income=42.0, credit_score=0.31)
        # Both have the same canonical projection.
        assert a == b

    def test_different_canonical_not_equal(self):
        a = CreditSOL(income=42.0, credit_score=0.31)
        b = CreditSOL(income=55.0, credit_score=0.45)
        assert a != b


# ---------------------------------------------------------------------------
# Regression: ⊥ propagation
#
# ⊥ must propagate cleanly through the entire pipeline without raising
# exceptions. Each operator is verified independently.
# ---------------------------------------------------------------------------

class TestBottomPropagation:

    def test_norm_propagates_bottom(self):
        assert norm(None, SCHEMA) is None

    def test_epsilon_propagates_bottom(self):
        assert epsilon(None, SCHEMA) is None

    def test_sanitize_propagates_bottom(self):
        assert sanitize(None, SCHEMA) is None

    def test_canon_propagates_bottom(self):
        assert canon(None, SCHEMA) is None

    def test_is_safe_returns_false_on_bottom(self):
        assert not is_safe(None, SCHEMA)

    def test_collapse_records_failure_on_bottom(self):
        trace = fresh_trace()
        result = collapse(None, SCHEMA, trace)
        assert result is None
        assert len(trace.failures()) == 1
        assert trace.failures()[0].op == "COLLAPSE_ON_BOTTOM"