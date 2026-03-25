"""
sol.py
------
The Structured Orchestrated Language (SOL) representational substrate.

SOL defines the constitutional object space R: the typed, finite, invariant-
addressable structures that the canonical pipeline operates over. Every
committed state in the constitutional architecture is a SOL object.

Formal definition (from the paper)
-----------------------------------
An SOL object is a finite set of typed attribute-value pairs satisfying a
domain schema Σ:

    x = { (k1 : τ1 = v1), (k2 : τ2 = v2), ..., (kn : τn = vn) }

where each k_i is an attribute identifier, τ_i a type drawn from a finite
type vocabulary T, and v_i a value in the domain of τ_i.

An SOL object is well-formed with respect to Σ iff:
    WF(x) ⟺ x ⊨ Σ

The representational space R is:
    - Symbolic or semi-symbolic (structured attribute graphs, not vectors)
    - Finite and enumerable (each object has finitely many attributes)
    - Invariant-addressable (each invariant is a decidable predicate over
      the typed structure)

Architecture of this module
----------------------------
SOLObject     Abstract base class. Defines the interface that all domain-
              specific SOL classes must satisfy: as_dict(), canonical(),
              is_well_formed(), and check_invariants(). The base class
              deliberately enforces no domain invariants — those are the
              responsibility of subclasses.

TaskSOL       Original minimal domain (task/priority). Retained for
              backwards compatibility with the existing test suite and
              run_example.py. Demonstrates the interface on a simple schema.

CreditSOL     Credit-scoring domain. Instantiates Table 1 of the paper in
              full: the four-field schema, the two-phase invariant check
              (per-attribute Inv1/Inv2 via the pipeline, global Inv3/Inv4
              enforced here at the object level as a second enforcement
              point), and a canonical() method that returns only the fields
              that survive full canonicalization.

Relationship to pipeline.py
----------------------------
SOL objects are the input and output type of the canonical pipeline.
pipeline.canon() operates on plain dicts (SOLDict) for generality; SOL
classes provide the typed, schema-aware wrapper that domain engineers work
with directly. The typical flow is:

    raw text
        → RELCompiler.compile()     → dict (with _provenance)
        → CreditSOL.from_dict()     → CreditSOL instance
        → sol.as_dict()             → SOLDict (stripped of internals)
        → pipeline.canon()          → canonical SOLDict
        → trace.commit()            → TraceEntry

The invariant checks in CreditSOL.check_invariants() are the object-level
second enforcement point described in the paper: they complement the
pipeline's Sanitize operator rather than replacing it. A representation
must satisfy both to be eligible for commitment.
"""

from __future__ import annotations

import abc
import copy
from typing import Any

from credit_invariants import (
    GLOBAL_INVARIANTS,
    PER_ATTRIBUTE_INVARIANTS,
)


# ---------------------------------------------------------------------------
# SOLObject — abstract base class
# ---------------------------------------------------------------------------

class SOLObject(abc.ABC):
    """
    Abstract base class for all SOL domain objects.

    Subclasses must implement:
        as_dict()           Return the object as a plain SOLDict, including
                            all fields regardless of canonical status. Used
                            as input to the pipeline.

        canonical()         Return only the fields that survive full
                            canonicalization for this domain. This is the
                            object-level view of Canon(x).

        is_well_formed()    Return True iff the object satisfies WF(x) with
                            respect to its domain schema. This is Inv4 at
                            the object level.

        check_invariants()  Return a list of (inv_id, satisfied, reason)
                            triples — one per invariant in the domain. Used
                            by the test suite and for audit reporting.
                            Does not raise; surfaces violations as data.

    The base class provides:
        __repr__            Human-readable representation for debugging.
        __eq__              Structural equality over canonical() output,
                            matching the paper's equivalence relation:
                            x ≈ y ⟺ Canon(x) = Canon(y).
    """

    @abc.abstractmethod
    def as_dict(self) -> dict[str, Any]:
        """Return the full object as a plain dict (pre-canonicalization)."""
        ...

    @abc.abstractmethod
    def canonical(self) -> dict[str, Any]:
        """Return the canonical form of this object."""
        ...

    @abc.abstractmethod
    def is_well_formed(self) -> bool:
        """Return True iff the object satisfies WF(x)."""
        ...

    @abc.abstractmethod
    def check_invariants(self) -> list[tuple[str, bool, str]]:
        """
        Return a list of (inv_id, satisfied, reason) triples.

        satisfied=True  → invariant holds; reason is ''.
        satisfied=False → invariant violated; reason explains why.

        This method does not raise. It surfaces all invariant states as
        data so that callers can inspect, log, and route them appropriately.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()!r})"

    def __eq__(self, other: object) -> bool:
        """
        Structural equality over canonical forms.

        Implements the paper's equivalence relation:
            x ≈ y ⟺ Canon(x) = Canon(y)

        Two SOL objects of different domain types are never equal, even if
        their canonical dicts happen to match — domain identity is part of
        constitutional identity.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.canonical() == other.canonical()


# ---------------------------------------------------------------------------
# TaskSOL — original minimal domain, retained for backwards compatibility
# ---------------------------------------------------------------------------

class TaskSOL(SOLObject):
    """
    Minimal task-priority domain. Retained from the original implementation.

    Schema:
        task     : string  (required)
        priority : enum {low, medium, high}  (required)

    Canonical basis: {task, priority} — both fields survive canonicalization.
    No proxy or drift-prone attributes; no global relational invariants.
    This domain exists to demonstrate the interface cleanly before the
    credit-scoring domain introduces full two-phase invariant enforcement.
    """

    VALID_PRIORITIES = {"low", "medium", "high"}

    def __init__(self, task: str, priority: str) -> None:
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"task must be a non-empty string, got {task!r}")
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {sorted(self.VALID_PRIORITIES)}, "
                f"got {priority!r}"
            )
        self._task = task.strip()
        self._priority = priority

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskSOL:
        """Construct from a plain dict (e.g. REL output)."""
        return cls(task=d["task"], priority=d["priority"])

    def as_dict(self) -> dict[str, Any]:
        return {"task": self._task, "priority": self._priority}

    def canonical(self) -> dict[str, Any]:
        # All fields are in the canonical basis for this domain.
        return {"task": self._task, "priority": self._priority}

    def is_well_formed(self) -> bool:
        return (
            isinstance(self._task, str)
            and bool(self._task.strip())
            and self._priority in self.VALID_PRIORITIES
        )

    def check_invariants(self) -> list[tuple[str, bool, str]]:
        """
        TaskSOL has no proxy, drift, or relational invariants beyond WF.
        Returns a single WF check.
        """
        wf = self.is_well_formed()
        return [
            ("WF", wf, "" if wf else "Object is not well-formed"),
        ]


# ---------------------------------------------------------------------------
# CreditSOL — full credit-scoring domain implementing Table 1
# ---------------------------------------------------------------------------

class CreditSOL(SOLObject):
    """
    Credit-scoring domain SOL object. Implements Table 1 of the paper:

        Inv1  ¬∃f ∈ Features(x) : Proxy(f)        Fairness     per-attribute
        Inv2  ¬∃f ∈ Features(x) : LatentDrift(f)  Robustness   per-attribute
        Inv3  Monotonic(income → score)            Validity     global
        Inv4  WF(x)                                Structural   global

    Schema (from credit_sl_spec.yaml):
        income         : float   required   canonical
        zip_code       : string  optional   protected_proxy   → pruned by Inv1
        latent_cluster : int     optional   latent_drift      → pruned by Inv2
        credit_score   : float   required   canonical

    Canonical basis: {income, credit_score}

    Two-phase invariant enforcement
    --------------------------------
    Per-attribute invariants (Inv1, Inv2) are enforced at the pipeline
    level by Sanitize Phase 1, and reflected here in canonical() which
    returns only the canonical basis fields. check_invariants() reports
    their status over the full (pre-pruning) object for audit purposes.

    Global invariants (Inv3, Inv4) are enforced at the pipeline level by
    Sanitize Phase 2, and enforced here as a second enforcement point in
    is_well_formed() and check_invariants(). Per the paper, this dual
    enforcement is deliberate: object-level checks provide a governed
    surface for domain engineers that is independent of the pipeline's
    convergence behaviour.

    Decidability note on Inv3
    -------------------------
    See credit_invariants.py. The per-object instantiation verified here
    checks necessary conditions (income > 0, credit_score ∈ [0, 1]) rather
    than the full functional monotonicity property. This limitation is
    documented in the module docstring and in the paper.
    """

    # Fields that survive full canonicalization (B_R for this domain).
    _CANONICAL_FIELDS = {"income", "credit_score"}

    # Fields that are in the schema but not in the canonical basis —
    # their presence is expected pre-pipeline and logged, not raised.
    _SCHEMA_FIELDS = {"income", "zip_code", "latent_cluster", "credit_score"}

    def __init__(
        self,
        income: float,
        credit_score: float,
        zip_code: str | None = None,
        latent_cluster: int | None = None,
    ) -> None:
        self._income = income
        self._credit_score = credit_score
        self._zip_code = zip_code
        self._latent_cluster = latent_cluster

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CreditSOL:
        """
        Construct from a plain dict (e.g. REL output or pipeline intermediate).

        Unknown keys are silently dropped — this mirrors the Lower stage
        behaviour and ensures that _provenance and _epsilon_failures metadata
        keys do not pollute the SOL object.
        """
        return cls(
            income=d["income"],
            credit_score=d["credit_score"],
            zip_code=d.get("zip_code"),
            latent_cluster=d.get("latent_cluster"),
        )

    def as_dict(self) -> dict[str, Any]:
        """
        Return the full object as a plain dict, including all fields that
        were present at construction time. This is the pre-pipeline view —
        non-canonical fields are included so that Sanitize has something
        to prune.
        """
        d: dict[str, Any] = {
            "income": self._income,
            "credit_score": self._credit_score,
        }
        if self._zip_code is not None:
            d["zip_code"] = self._zip_code
        if self._latent_cluster is not None:
            d["latent_cluster"] = self._latent_cluster
        return d

    def canonical(self) -> dict[str, Any]:
        """
        Return only the canonical basis fields {income, credit_score}.

        This is the object-level view of Canon(x) for this domain.
        Non-canonical fields (zip_code, latent_cluster) are excluded
        regardless of whether they are present in the object.

        Note: this method does not verify that Inv3 and Inv4 hold over
        the canonical fields — it returns the canonical projection
        unconditionally. Use check_invariants() to verify safety before
        commitment.
        """
        return {
            "income": self._income,
            "credit_score": self._credit_score,
        }

    def is_well_formed(self) -> bool:
        """
        Return True iff the canonical projection satisfies WF(x) ∧ Inv3.

        This is the object-level second enforcement point for the global
        invariants. It checks:
            - income is a positive numeric (necessary condition for Inv3)
            - credit_score is in [0, 1] (necessary condition for Inv3)
            - Both required fields are present and correctly typed (Inv4)
        """
        if not isinstance(self._income, (int, float)) or self._income <= 0:
            return False
        if not isinstance(self._credit_score, (int, float)):
            return False
        if not (0.0 <= self._credit_score <= 1.0):
            return False
        return True

    def check_invariants(self) -> list[tuple[str, bool, str]]:
        """
        Return the full invariant status report for this object.

        Evaluates all four invariants from Table 1 and returns one triple
        per invariant. Per-attribute invariants (Inv1, Inv2) are checked
        over the full (pre-canonical) object; global invariants (Inv3, Inv4)
        are checked over the canonical projection.

        This method is the primary interface for the test suite's axiom
        verification and for audit reporting. It does not raise.
        """
        results: list[tuple[str, bool, str]] = []
        full = self.as_dict()

        # -- Per-attribute invariants (Inv1, Inv2) ---------------------
        # We load the schema here for the predicate interface.
        # In production, schema would be injected; for the reference
        # implementation we load it directly.
        import yaml
        with open("credit_sl_spec.yaml", "r") as f:
            schema = yaml.safe_load(f)

        for inv_id, predicate in PER_ATTRIBUTE_INVARIANTS:
            violations = []
            for field_name, field_value in full.items():
                if not predicate(field_name, field_value, schema):
                    violations.append(field_name)
            if violations:
                results.append((
                    inv_id,
                    False,
                    f"Fields violating {inv_id}: {violations}",
                ))
            else:
                results.append((inv_id, True, ""))

        # -- Global invariants (Inv3, Inv4) over canonical projection ---
        canonical = self.canonical()
        for inv_id, predicate in GLOBAL_INVARIANTS:
            satisfied, reason = predicate(canonical, schema)
            results.append((inv_id, satisfied, reason))

        return results