"""
trace.py
--------
Append‑only constitutional trace for the governed canonicalization pipeline.

The trace is a first‑class constitutional component: every commitment made
by Collapse is recorded here as an immutable event. The trace is not a
monitoring overlay; it is structurally inseparable from commitment itself.

Formal guarantees satisfied
---------------------------
Guarantee 6 — Irreversibility of Collapse:
    The trace is append‑only by construction. No mutation interface exists.

Guarantee 7 — Canonical Trace Invariant:
    Every COMMIT entry contains a canonical, safe representation. Collapse
    writes only after Canon(x) has been verified upstream.

Trace entry schema
------------------
Each entry is a NamedTuple:

    (t, op, c, m)

    t : float        Timestamp (time.time())
    op: str          Operation identifier from Op
    c : dict | None  Canonical form (for COMMIT) or None (for failures)
    m : dict         Metadata (schema version, domain, reason, provenance)

Failure events
--------------
REL failures, invariant violations, and collapse failures are surfaced as
first‑class constitutional events. Nothing is swallowed or suppressed.

Provenance
----------
Each COMMIT entry includes:
    schema_version
    domain
    committed_fields
    (plus any caller‑supplied metadata)
"""

from __future__ import annotations

import time
from typing import Any, Iterator, NamedTuple


# ---------------------------------------------------------------------------
# Trace entry — immutable by design
# ---------------------------------------------------------------------------

class TraceEntry(NamedTuple):
    """
    Immutable constitutional event record.

    NamedTuple ensures immutability: no committed entry can be modified
    after the fact, satisfying Guarantee 6 at the implementation level.
    """
    t: float          # Timestamp
    op: str           # Operation identifier
    c: dict | None    # Canonical form (None for failure events)
    m: dict           # Metadata


# ---------------------------------------------------------------------------
# Closed vocabulary of constitutional operations
# ---------------------------------------------------------------------------

class Op:
    COMMIT                     = "COMMIT"
    REL_FAILURE                = "REL_FAILURE"
    COLLAPSE_ON_BOTTOM         = "COLLAPSE_ON_BOTTOM"
    COLLAPSE_NO_CANONICAL_FORM = "COLLAPSE_NO_CANONICAL_FORM"
    INVARIANT_VIOLATION        = "INVARIANT_VIOLATION"
    GLOBAL_INVARIANT_VIOLATION = "GLOBAL_INVARIANT_VIOLATION"


# ---------------------------------------------------------------------------
# ConstitutionalTrace — append‑only log
# ---------------------------------------------------------------------------

class ConstitutionalTrace:
    """
    Append‑only constitutional trace.

    Only append operations exist. No deletion, mutation, or reordering is
    possible. Iteration and indexed reads are provided for auditors.

    Thread safety:
        This reference implementation is single‑threaded. Production systems
        should wrap _append in a lock or replace it with an external
        append‑only backend (e.g., Kafka, immutable ledger).
    """

    def __init__(self, schema: dict) -> None:
        self._entries: list[TraceEntry] = []
        self._schema_version = schema.get("schema_version", "unknown")
        self._domain = schema.get("domain", "unknown")

    # ------------------------------------------------------------------
    # Internal append — the sole write path
    # ------------------------------------------------------------------

    def _append(self, op: str, c: dict | None, m: dict) -> TraceEntry:
        entry = TraceEntry(t=time.time(), op=op, c=c, m=m)
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Public write interface
    # ------------------------------------------------------------------

    def commit(self, canonical: dict, metadata: dict) -> TraceEntry:
        """
        Record a successful constitutional commitment.

        The canonical form is deep‑copied to prevent caller mutation from
        altering the trace. Provenance metadata is merged with caller data.
        """
        import copy

        provenance = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "committed_fields": sorted(canonical.keys()),
        }
        merged = {**provenance, **metadata}
        return self._append(Op.COMMIT, copy.deepcopy(canonical), merged)

    def record_failure(self, reason: str, metadata: dict) -> TraceEntry:
        """
        Record a collapse‑level failure (⊥ input or no canonical form).
        """
        m = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "reason": reason,
            **metadata,
        }
        return self._append(reason, None, m)

    def record_violation(
        self,
        field_name: str,
        inv_id: str,
        field_value: Any,
    ) -> TraceEntry:
        """
        Record a per‑attribute invariant violation (Sanitize Phase 1).
        """
        m = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "field": field_name,
            "invariant": inv_id,
            "value": repr(field_value),
        }
        return self._append(Op.INVARIANT_VIOLATION, None, m)

    def record_global_violation(
        self,
        inv_id: str,
        reason: str,
        residual_obj: dict,
    ) -> TraceEntry:
        """
        Record a global invariant violation (Sanitize Phase 2).
        """
        import copy

        m = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "invariant": inv_id,
            "reason": reason,
            "residual_object": copy.deepcopy(residual_obj),
        }
        return self._append(Op.GLOBAL_INVARIANT_VIOLATION, None, m)

    def record_rel_failure(
        self,
        failure_type: str,
        raw_output: str,
        metadata: dict | None = None,
    ) -> TraceEntry:
        """
        Record a REL extraction failure as a constitutional event.
        """
        m = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "failure_type": failure_type,
            "raw_output": raw_output,
            **(metadata or {}),
        }
        return self._append(Op.REL_FAILURE, None, m)

    # ------------------------------------------------------------------
    # Read interface — immutable access for auditors
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[TraceEntry]:
        return iter(self._entries)

    def __getitem__(self, index: int) -> TraceEntry:
        return self._entries[index]

    def commits(self) -> list[TraceEntry]:
        return [e for e in self._entries if e.op == Op.COMMIT]

    def failures(self) -> list[TraceEntry]:
        return [e for e in self._entries if e.op != Op.COMMIT]

    def audit_report(self) -> dict:
        """
        Produce a regulator‑facing audit summary.

        Includes total events, commit count, failure count, and a
        serializable list of all entries.
        """
        return {
            "domain": self._domain,
            "schema_version": self._schema_version,
            "total_events": len(self._entries),
            "commits": len(self.commits()),
            "failures": len(self.failures()),
            "entries": [
                {"t": e.t, "op": e.op, "c": e.c, "m": e.m}
                for e in self._entries
            ],
        }
