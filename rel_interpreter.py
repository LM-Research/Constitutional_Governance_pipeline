"""
rel_interpreter.py
------------------
Regex‑based REL front‑end implementing the same four‑stage architecture as
rel_compiler.py:

    REL_regex : Y → R_Σ ∪ {⊥}

This module is intended for domains where extraction is naturally expressed
as regular‑expression capture rather than tokenization. It preserves the
REL guarantees:

    - Deterministic
    - Total
    - Schema‑driven
    - Auditable
    - First‑class failure taxonomy

Each rule in the SL spec must define:
    name:     field name
    pattern:  regex with exactly one capture group
    required: boolean (default: False)
    default:  fallback value if optional and missing

The four stages mirror the canonical REL pipeline:

    1. Lex        → run all regex patterns, collect raw matches
    2. Parse      → enforce required fields, normalize keys
    3. TypeCheck  → enforce schema types, coercions, defaults
    4. Lower      → project into SOL vocabulary + provenance metadata
"""

from __future__ import annotations

import re
import time
from typing import Any, Literal, TypedDict

import yaml

# ---------------------------------------------------------------------------
# Failure taxonomy (shared with rel_compiler)
# ---------------------------------------------------------------------------

class FailureType:
    OMISSION                = "omission"
    MISCLASSIFICATION       = "misclassification"
    AMBIGUITY_COLLAPSE      = "ambiguity_collapse"
    SCHEMA_DRIFT            = "schema_drift"
    ADVERSARIAL_FORMATTING  = "adversarial_formatting"

FailureTypeLiteral = Literal[
    "omission",
    "misclassification",
    "ambiguity_collapse",
    "schema_drift",
    "adversarial_formatting",
]

class RELWarning(TypedDict, total=False):
    failure_type: FailureTypeLiteral | None
    field: str
    detail: str

class RELFailure(Exception):
    """Raised when REL cannot produce a syntactically sound extraction."""
    def __init__(
        self,
        failure_type: FailureTypeLiteral,
        field: str,
        raw_output: str,
        detail: str,
    ) -> None:
        self.failure_type = failure_type
        self.field = field
        self.raw_output = raw_output
        self.detail = detail
        super().__init__(f"[{failure_type}] field={field!r}: {detail}")


REL_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Load SL spec (regex‑based)
# ---------------------------------------------------------------------------

def load_spec(path: str = "sl_spec.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Stage 1 — Lex (Regex Extraction)
#
# For each rule:
#   - Apply regex
#   - If match: record raw_value
#   - If no match and required: omission failure
#   - If no match and optional: use default
#
# Output: dict[str, Any] of raw extracted values
# ---------------------------------------------------------------------------

def lex_regex(raw: str, sl_spec: dict) -> dict[str, Any]:
    """
    Stage 1: apply regex rules to raw text.

    Returns a dict of {field_name: raw_value or default}.
    Raises RELFailure(omission) if a required field is missing.
    """
    result: dict[str, Any] = {}

    for rule in sl_spec["rules"]:
        name = rule["name"]
        pattern = rule["pattern"]
        required = rule.get("required", False)
        default = rule.get("default")

        match = re.search(pattern, raw)
        if match:
            result[name] = match.group(1)
        else:
            if required:
                raise RELFailure(
                    FailureType.OMISSION,
                    field=name,
                    raw_output=raw,
                    detail=f"Missing required field '{name}' via regex rule",
                )
            result[name] = default

    return result


# ---------------------------------------------------------------------------
# Stage 2 — Parse
#
# Regex extraction already produces a dict, but we normalize keys and
# preserve unknown fields for schema_drift detection in TypeCheck.
# ---------------------------------------------------------------------------

def parse_regex(
    extracted: dict[str, Any],
    schema: dict,
    raw: str,
    warnings: list[RELWarning],
) -> dict[str, Any]:
    """
    Stage 2: normalize keys and prepare candidate dict.
    """
    result: dict[str, Any] = {}

    for key, value in extracted.items():
        normalised = key.lower().replace(" ", "_")
        result[normalised] = value

    return result


# ---------------------------------------------------------------------------
# Stage 3 — TypeCheck (shared semantics with rel_compiler)
# ---------------------------------------------------------------------------

_TYPE_COERCIONS: dict[str, type] = {
    "float":  float,
    "int":    int,
    "string": str,
}

def typecheck_regex(
    candidate: dict[str, Any],
    schema: dict,
    raw: str,
    warnings: list[RELWarning],
) -> dict[str, Any]:
    """
    Stage 3: enforce schema-level type constraints.
    """
    field_map = {f["name"]: f for f in schema["fields"]}
    result: dict[str, Any] = {}

    for key, value in candidate.items():
        if key not in field_map:
            warnings.append(RELWarning(
                failure_type=FailureType.SCHEMA_DRIFT,
                field=key,
                detail=f"Field '{key}' not in SL schema",
            ))
            continue

        spec = field_map[key]
        declared = spec.get("type", "string")
        target = _TYPE_COERCIONS.get(declared)

        if target is None or isinstance(value, target):
            result[key] = value
            continue

        try:
            result[key] = target(value)
        except (ValueError, TypeError):
            default = spec.get("default")
            if default is not None:
                result[key] = default
                warnings.append(RELWarning(
                    failure_type=FailureType.MISCLASSIFICATION,
                    field=key,
                    detail=f"Cannot coerce '{key}' to {declared}; using default",
                ))
            else:
                raise RELFailure(
                    FailureType.MISCLASSIFICATION,
                    field=key,
                    raw_output=raw,
                    detail=f"Cannot coerce '{key}' value {value!r} to {declared}",
                )

    return result


# ---------------------------------------------------------------------------
# Stage 4 — Lower (shared semantics with rel_compiler)
# ---------------------------------------------------------------------------

def lower_regex(
    type_checked: dict[str, Any],
    schema: dict,
    model_version: str = "unknown",
) -> dict[str, Any]:
    """
    Stage 4: project into SOL canonical vocabulary + provenance metadata.
    """
    field_names = {f["name"] for f in schema["fields"]}
    aliases = {f["name"]: f.get("alias", f["name"]) for f in schema["fields"]}

    result: dict[str, Any] = {}

    for key, value in type_checked.items():
        canonical = aliases.get(key, key)
        if canonical in field_names:
            result[canonical] = value

    result["_provenance"] = {
        "rel_version": REL_VERSION,
        "sl_spec_version": schema.get("schema_version", "unknown"),
        "model_version": model_version,
        "extraction_timestamp": time.time(),
        "domain": schema.get("domain", "unknown"),
        "frontend": "regex",
    }

    return result


# ---------------------------------------------------------------------------
# RELRegexCompiler — full four-stage regex-based REL
# ---------------------------------------------------------------------------

class RELRegexCompiler:
    """
    Regex-based REL front-end implementing the same four-stage architecture
    as rel_compiler.py, but using regex rules instead of tokenization.

    Usage:
        compiler = RELRegexCompiler.from_spec("credit_sl_spec.yaml")
        sol_dict = compiler.compile(raw_text)
    """

    def __init__(self, sl_spec: dict, model_version: str = "unknown") -> None:
        self.sl_spec = sl_spec
        self.schema = sl_spec  # same structure as SL spec
        self.model_version = model_version

    @classmethod
    def from_spec(cls, path: str, model_version: str = "unknown") -> RELRegexCompiler:
        return cls(load_spec(path), model_version)

    def compile(
        self,
        raw: str,
    ) -> dict[str, Any]:
        """
        Run all four stages and return the lowered SOL dict.
        Raises RELFailure on any fatal extraction error.
        """
        warnings: list[RELWarning] = []

        # Stage 1: Lex (regex extraction)
        extracted = lex_regex(raw, self.sl_spec)

        # Stage 2: Parse
        candidate = parse_regex(extracted, self.schema, raw, warnings)

        # Stage 3: TypeCheck
        type_checked = typecheck_regex(candidate, self.schema, raw, warnings)

        # Stage 4: Lower
        lowered = lower_regex(type_checked, self.schema, self.model_version)

        return lowered
