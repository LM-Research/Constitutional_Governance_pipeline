"""
trace.py
--------
The constitutional append-only trace layer.

Every commitment made by Collapse is recorded here as a constitutional act.
The trace is not a monitoring overlay; it is structurally inseparable from
commitment itself. Disabling the trace disables Collapse.

Formal guarantee satisfied
--------------------------
Guarantee 7 (Canonical Trace Invariant): every entry in the trace is a
canonical, safe representation. This holds because Collapse writes to the
trace only after Canon(x) has been verified — the trace layer itself
imposes no additional safety check, and requires none: the invariant is
satisfied upstream by construction.

Guarantee 6 (Irreversibility of Collapse): the trace is append-only by
architectural specification, not by policy. The append-only constraint is
enforced here by exposing no mutation interface. There is no delete(),
no update(), no __setitem__. An auditor reading the trace reads exactly
what was committed, in the order it was committed.

Trace entry schema
------------------
Each entry is a named tuple with four fields, matching the formal definition:

    (t, op, c, m)

    t   : float       ISO timestamp (time.time()) of the commitment act
    op  : str         Operation name — "COMMIT", "REL_FAILURE",
                      "COLLAPSE_ON_BOTTOM", "COLLAPSE_NO_CANONICAL_FORM",
                      "INVARIANT_VIOLATION", "GLOBAL_INVARIANT_VIOLATION"
    c   : dict | None The canonical form committed, or None for failure events
    m   : dict        Metadata — agent id, schema version, provenance, reason

Failure events
--------------
REL failures and Sanitize violations are surfaced as first-class trace
events rather than exceptions or silent drops. This directly supports
Article 9's continuous lifecycle monitoring requirement: every anomaly
is visible and auditable, never suppressed.

Provenance
----------
Each COMMIT entry carries provenance metadata:
    schema_version  : str   from the SL spec
    domain          : str   from the SL spec
    committed_fields: list  the field names present in the canonical form

This provides auditors with a complete chain of custody from extraction
through commitment, as described in Section 3 of the paper.
"""

from __future__ import annotations

import time
from typing import Any, Iterator, NamedTuple


# ---------------------------------------------------------------------------
# Trace entry
# ---------------------------------------------------------------------------

class TraceEntry(NamedTuple):
    """
    Immutable record of a single constitutional event.

    Fields match the formal (t, op, c, m) schema exactly.
    NamedTuple is used rather than dataclass to make entries truly immutable:
    there is no mechanism by which a committed entry can be modified after
    the fact, which is the implementation-level guarantee of Guarantee 6.
    """
    t: float          # Timestamp: time.time() at moment of commitment
    op: str           # Operation identifier
    c: dict | None    # Canonical form, or None for non-commit events
    m: dict           # Metadata dict


# ---------------------------------------------------------------------------
# Operation constants
# Defined here so callers never pass raw strings, making the trace auditable
# against a closed vocabulary of constitutional events.
# ---------------------------------------------------------------------------

class Op:
    COMMIT                       = "COMMIT"
    REL_FAILURE                  = "REL_FAILURE"
    COLLAPSE_ON_BOTTOM           = "COLLAPSE_ON_BOTTOM"
    COLLAPSE_NO_CANONICAL_FORM   = "COLLAPSE_NO_CANONICAL_FORM"
    INVARIANT_VIOLATION          = "INVARIANT_VIOLATION"
    GLOBAL_INVARIANT_VIOLATION   = "GLOBAL_INVARIANT_VIOLATION"


# ---------------------------------------------------------------------------
# ConstitutionalTrace
# ---------------------------------------------------------------------------

class ConstitutionalTrace:
    """
    Append-only constitutional trace.

    The only write operation is append (via the internal _append method).
    No public interface permits deletion, modification, or reordering of
    entries. Iteration and indexed read access are provided for auditors.

    Thread safety: this implementation is single-threaded. Production
    deployments should wrap _append in a lock or use an external
    append-only log backend (e.g. a Kafka topic, an immutable ledger).
    The interface is designed so that swap-out is straightforward: replace
    _append with a write to the external backend and __iter__ / __len__
    with reads from it.
    """

    def __init__(self, schema: dict) -> None:
        """
        Initialise the trace for a given SL schema.

        The schema is stored for provenance metadata on each COMMIT entry.
        """
        self._entries: list[TraceEntry] = []
        self._schema_version: str = schema.get("schema_version", "unknown")
        self._domain: str = schema.get("domain", "unknown")

    # ------------------------------------------------------------------
    # Internal append — the only write path.
    # All public methods route through here.
    # ------------------------------------------------------------------

    def _append(self, op: str, c: dict | None, m: dict) -> TraceEntry:
        """
        Append a new entry to the trace. Returns the entry for caller inspection.

        This is the sole write path. Callers outside this class should use
        the public methods (commit, record_failure, etc.) rather than
        calling _append directly, so that the operation vocabulary remains
        governed by the Op constants above.
        """
        entry = TraceEntry(t=time.time(), op=op, c=c, m=m)
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Public write interface
    # ------------------------------------------------------------------

    def commit(self, canonical: dict, metadata: dict) -> TraceEntry:
        """
        Record a successful constitutional commitment.

        Called exclusively by Collapse after Canon(x) has been verified.
        The canonical form is deep-copied before storage so that subsequent
        mutation of the caller's dict cannot alter the trace record.

        Provenance metadata (schema version, domain, committed fields) is
        merged with any caller-supplied metadata.
        """
        import copy
        provenance = {
            "schema_version": self._schema_version,
            "domain": self._domain,
            "committed_fields": sorted(canonical.keys()),
        }
        m = {**provenance, **metadata}
        return self._append(Op.COMMIT, copy.deepcopy(canonical), m)

    def record_failure(self, reason: str, metadata: dict) -> TraceEntry:
        """
        Record a Collapse-level failure event (⊥ input or no canonical form).
        c is None: no canonical form was committed.
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
        Record a per-attribute invariant violation surfaced during Sanitize
        Phase 1. The field is being pruned; this entry documents why.
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
        Record a global invariant violation surfaced during Sanitize Phase 2.
        The residual object (post Phase 1 pruning) is recorded in full so
        that auditors can inspect what remained when the global check failed.
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
        Record a REL extraction failure as a first-class constitutional event.

        failure_type should be drawn from the bounded error taxonomy in the
        paper: omission, misclassification, ambiguity_collapse, schema_drift,
        adversarial_formatting, distribution_shift.

        raw_output is the unprocessed model emission that triggered the
        failure, preserved for post-hoc auditing against extraction behaviour.
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
    # Read interface — for auditors and tests
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[TraceEntry]:
        """Iterate over entries in commitment order (oldest first)."""
        return iter(self._entries)

    def __getitem__(self, index: int) -> TraceEntry:
        """Read access by index. No write path exposed."""
        return self._entries[index]

    def commits(self) -> list[TraceEntry]:
        """Return only successful COMMIT entries, in order."""
        return [e for e in self._entries if e.op == Op.COMMIT]

    def failures(self) -> list[TraceEntry]:
        """Return all non-COMMIT entries (violations, failures), in order."""
        return [e for e in self._entries if e.op != Op.COMMIT]

    def audit_report(self) -> dict:
        """
        Return a summary dict suitable for a regulator-facing audit report.

        Provides: total events, commit count, failure count, and the full
        entry list serialised to plain dicts for JSON export.
        """
        return {
            "domain": self._domain,
            "schema_version": self._schema_version,
            "total_events": len(self._entries),
            "commits": len(self.commits()),
            "failures": len(self.failures()),
            "entries": [
                {
                    "t": e.t,
                    "op": e.op,
                    "c": e.c,
                    "m": e.m,
                }
                for e in self._entries
            ],
        }