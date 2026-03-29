"""
sol.py
------
The Structured Orchestrated Language (SOL) representational substrate.

SOL defines the constitutional object space R: the typed, finite,
invariant‑addressable structures that the canonical pipeline operates over.
Every committed state in the constitutional architecture is a SOL object.

Formal definition (from the paper)
----------------------------------
An SOL object is a finite set of typed attribute–value pairs satisfying a
domain schema Σ:

    x = { (k1 : τ1 = v1), ..., (kn : τn = vn) }

WF(x) holds iff x satisfies Σ. Invariants are decidable predicates over
the typed structure. Canonicalization is a projection onto a domain’s
canonical basis B_R.

This module provides:
    - SOLObject: abstract base class
    - TaskSOL:   minimal task domain
    - CreditSOL: full credit‑scoring domain (Table 1)
"""

from __future__ import annotations

import abc
from typing import Any, Callable


# ---------------------------------------------------------------------------
# SOLObject — abstract base class
# ---------------------------------------------------------------------------

class SOLObject(abc.ABC):
    """
    Abstract base class for all SOL domain objects.

    Subclasses must implement:
        as_dict()          → full pre‑canonical representation
        canonical()        → projection onto canonical basis B_R
        is_well_formed()   → schema‑level WF(x)
        check_invariants() → full invariant report (Inv1–Inv4)

    The base class provides:
        __eq__             → structural equality over canonical forms
        __repr__           → debugging representation

    Two SOL objects are equal iff their canonical projections match and
    they belong to the same domain class.
    """

    # Each subclass must define a class‑level schema dict.
    schema: dict[str, Any] = {}

    @classmethod
    def get_schema(cls) -> dict[str, Any]:
        """Return the domain schema Σ."""
        return cls.schema

    @abc.abstractmethod
    def as_dict(self) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def canonical(self) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def is_well_formed(self) -> bool:
        ...

    @abc.abstractmethod
    def check_invariants(self) -> list[tuple[str, bool, str]]:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.canonical() == other.canonical()


# ---------------------------------------------------------------------------
# TaskSOL — minimal domain
# ---------------------------------------------------------------------------

class TaskSOL(SOLObject):
    """
    Minimal task/priority domain.

    Schema:
        task     : string (required)
        priority : string ∈ {low, medium, high}

    Canonical basis: {task, priority}
    """

    schema = {
        "fields": [
            {"name": "task", "type": "string", "required": True},
            {"name": "priority", "type": "string", "required": True},
        ],
        "canonical_basis": ["task", "priority"],
    }

    VALID_PRIORITIES = {"low", "medium", "high"}

    def __init__(self, task: str, priority: str) -> None:
        self._task = task
        self._priority = priority

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskSOL:
        return cls(task=d["task"], priority=d["priority"])

    def as_dict(self) -> dict[str, Any]:
        return {"task": self._task, "priority": self._priority}

    def canonical(self) -> dict[str, Any]:
        return {"task": self._task, "priority": self._priority}

    def is_well_formed(self) -> bool:
        return (
            isinstance(self._task, str)
            and bool(self._task.strip())
            and self._priority in self.VALID_PRIORITIES
        )

    def check_invariants(self) -> list[tuple[str, bool, str]]:
        wf = self.is_well_formed()
        return [("WF", wf, "" if wf else "Object is not well‑formed")]


# ---------------------------------------------------------------------------
# CreditSOL — full credit‑scoring domain (Table 1)
# ---------------------------------------------------------------------------

class CreditSOL(SOLObject):
    """
    Credit‑scoring domain implementing Table 1:

        Inv1  ¬Proxy(f)
        Inv2  ¬LatentDrift(f)
        Inv3  Monotonic(income → score)  (per‑object necessary conditions)
        Inv4  WF(x)

    Canonical basis: {income, credit_score}
    """

    schema = {
        "fields": [
            {"name": "income", "type": "float", "required": True},
            {"name": "zip_code", "type": "string", "required": False},
            {"name": "latent_cluster", "type": "int", "required": False},
            {"name": "credit_score", "type": "float", "required": True},
        ],
        "canonical_basis": ["income", "credit_score"],
    }

    CANONICAL_FIELDS = {"income", "credit_score"}

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
        return cls(
            income=d["income"],
            credit_score=d["credit_score"],
            zip_code=d.get("zip_code"),
            latent_cluster=d.get("latent_cluster"),
        )

    # ------------------------------------------------------------------
    # Representations
    # ------------------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        d = {
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
        Projection onto the canonical basis B_R = {income, credit_score}.

        This method does *not* enforce Inv3 or Inv4 — it is a projection,
        not a safety check. Safety is enforced by the pipeline and by
        check_invariants().
        """
        return {
            "income": self._income,
            "credit_score": self._credit_score,
        }

    # ------------------------------------------------------------------
    # Well‑formedness (schema‑level only)
    # ------------------------------------------------------------------

    def is_well_formed(self) -> bool:
        """
        Schema‑level WF(x): required fields present and correctly typed.

        This does *not* enforce Inv3 (monotonicity conditions). Those are
        global invariants, not schema‑level WF.
        """
        if not isinstance(self._income, (int, float)):
            return False
        if not isinstance(self._credit_score, (int, float)):
            return False
        return True

    # ------------------------------------------------------------------
    # Invariant checks (Inv1–Inv4)
    # ------------------------------------------------------------------

    def check_invariants(self) -> list[tuple[str, bool, str]]:
        """
        Evaluate all four invariants from Table 1.

        Per‑attribute invariants (Inv1, Inv2) are evaluated over the full
        object. Global invariants (Inv3, Inv4) are evaluated over the
        canonical projection.
        """
        results: list[tuple[str, bool, str]] = []
        full = self.as_dict()
        schema = self.get_schema()

        # Load invariant predicates
        from credit_invariants import PER_ATTRIBUTE_INVARIANTS, GLOBAL_INVARIANTS

        # Inv1, Inv2 — per‑attribute
        for inv_id, predicate in PER_ATTRIBUTE_INVARIANTS:
            violations = [
                f for f, v in full.items()
                if not predicate(f, v, schema)
            ]
            if violations:
                results.append((inv_id, False, f"Violating fields: {violations}"))
            else:
                results.append((inv_id, True, ""))

        # Inv3, Inv4 — global
        canonical = self.canonical()
        for inv_id, predicate in GLOBAL_INVARIANTS:
            ok, reason = predicate(canonical, schema)
            results.append((inv_id, ok, reason))

        return results
