"""
rel_compiler.py
---------------
The Representation Extraction Layer (REL) implemented as a four-stage
deterministic compiler.

    REL : Y → R_Σ ∪ {⊥}

where Y is the space of model outputs (structured text or JSON) and R_Σ
is the space of SOL objects well-formed with respect to the domain schema Σ.
REL returns ⊥ on extraction failure.

The four stages
---------------
1. Lex       Segment the raw model output into a flat sequence of
             (key, raw_value) tokens. No type interpretation occurs here;
             the lexer operates on surface form only.

2. Parse     Construct a candidate attribute–value dict from the token
             sequence. Handles duplicate keys (last-value-wins, logged),
             unknown keys (retained for downstream filtering, logged), and
             missing required keys (raises RELFailure of type 'omission').

3. TypeCheck Enforce schema-level type constraints against Σ. Validates
             that each extracted value is coercible to its declared type.
             Values that fail coercion are either replaced with a schema
             default (if one exists) or flagged as 'misclassification'.

4. Lower     Deterministically project the type-checked dict into the SOL
             canonical attribute vocabulary defined by the SL spec. Renames
             aliased fields, drops fields not in the schema vocabulary, and
             attaches provenance metadata (REL version, SL spec version,
             model version, extraction timestamp).

Each stage is a pure function with a defined input and output type.
Stages are independently testable and independently auditable.

Failure taxonomy
----------------
REL failures are first-class constitutional events, not exceptions.
All failures are recorded in the trace via record_rel_failure() and
surfaced as RELFailure exceptions that callers are expected to catch
and route to the trace. The failure_type field is drawn from the
bounded error taxonomy in the paper:

    omission            Required attribute not present in model output
    misclassification   Attribute present but value not coercible to
                        declared type, and no default available
    ambiguity_collapse  Multiple valid interpretations; one selected
                        deterministically (logged, not fatal)
    schema_drift        SL spec does not cover a field present in output
    adversarial_formatting  Output structured to defeat extraction
                        (detected heuristically; see _lex_json)

Syntactic soundness vs. semantic completeness
---------------------------------------------
REL guarantees syntactic soundness: extracted attributes correctly
reflect the surface form of the model output. It does not guarantee
semantic completeness: attributes that are absent from the output
cannot be extracted. Incompleteness is treated as a first-class
failure mode (type: 'omission') propagated through the pipeline
rather than silently ignored.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Literal, TypedDict

import yaml


# ---------------------------------------------------------------------------
# REL version — recorded in provenance metadata on every extraction
# ---------------------------------------------------------------------------

REL_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Failure types — closed vocabulary matching the paper's taxonomy
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


# ---------------------------------------------------------------------------
# Warning structure — non-fatal observations collected during extraction
# ---------------------------------------------------------------------------

class RELWarning(TypedDict, total=False):
    failure_type: FailureTypeLiteral | None
    field: str
    detail: str


# ---------------------------------------------------------------------------
# RELFailure — the exception type for all extraction failures.
# Callers catch this and route to trace.record_rel_failure().
# ---------------------------------------------------------------------------

class RELFailure(Exception):
    """
    Raised when REL cannot produce a syntactically sound extraction.

    Attributes
    ----------
    failure_type : str      One of the FailureType constants above.
    field        : str      The field involved, or '' for structural failures.
    raw_output   : str      The raw model output that triggered the failure.
    detail       : str      Human-readable explanation for the trace record.
    """

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


# ---------------------------------------------------------------------------
# Stage 1: Lex
#
# Segment raw model output into a flat list of (key, raw_value) pairs.
# Two input formats are supported: structured text (Key: Value) and JSON.
# The lexer does not interpret types; raw_value is a string or primitive.
#
# Adversarial formatting detection is heuristic and conservative.
# ---------------------------------------------------------------------------

_TEXT_PATTERN = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9_ ]*?)\s*:\s*(?P<value>.+)$",
    re.MULTILINE,
)

_MAX_VALUE_LENGTH = 4096   # heuristic limit for adversarial formatting detection


def _lex_text(raw: str) -> list[tuple[str, str]]:
    """
    Lex structured text in 'Key: Value' format.

    Returns a list of (key, raw_value) pairs in document order.
    Raises RELFailure(adversarial_formatting) if structural anomalies
    are detected.
    """
    tokens: list[tuple[str, str]] = []

    for match in _TEXT_PATTERN.finditer(raw):
        key = match.group("key").strip()
        value = match.group("value").strip()

        if len(value) > _MAX_VALUE_LENGTH:
            raise RELFailure(
                FailureType.ADVERSARIAL_FORMATTING,
                field=key,
                raw_output=raw,
                detail=(
                    f"Value for '{key}' exceeds maximum length "
                    f"({len(value)} > {_MAX_VALUE_LENGTH})"
                ),
            )

        tokens.append((key, value))

    return tokens


def _lex_json(raw: str) -> list[tuple[str, Any]]:
    """
    Lex a JSON model output into (key, value) pairs.

    Only flat JSON objects are accepted. Nested structures are flagged as
    adversarial_formatting — the SOL representational space is a finite set
    of typed attribute-value pairs, not a recursive object graph.
    """
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RELFailure(
            FailureType.ADVERSARIAL_FORMATTING,
            field="",
            raw_output=raw,
            detail=f"JSON parse error: {e}",
        )

    if not isinstance(obj, dict):
        raise RELFailure(
            FailureType.ADVERSARIAL_FORMATTING,
            field="",
            raw_output=raw,
            detail="JSON input must be a flat object, not a list or scalar",
        )

    for k, v in obj.items():
        if isinstance(v, dict):
            raise RELFailure(
                FailureType.ADVERSARIAL_FORMATTING,
                field=k,
                raw_output=raw,
                detail=f"Nested object at '{k}' — SOL requires flat structure",
            )

    return list(obj.items())


def lex(raw: str, input_format: str = "text") -> list[tuple[str, Any]]:
    """
    Stage 1: segment raw model output into (key, raw_value) tokens.

    input_format: "text" (default) or "json".
    """
    if input_format == "json":
        return _lex_json(raw)
    return _lex_text(raw)


# ---------------------------------------------------------------------------
# Stage 2: Parse
#
# Construct a candidate attribute-value dict from the token sequence.
# Handles:
#   - Duplicate keys: last-value-wins (deterministic), logged as
#     ambiguity_collapse (non-fatal).
#   - Unknown keys: retained for schema_drift detection in TypeCheck.
#   - Missing required keys: raises RELFailure(omission).
#
# Non-fatal observations are appended to a warnings list.
# ---------------------------------------------------------------------------

def parse(
    tokens: list[tuple[str, Any]],
    schema: dict,
    raw: str,
    warnings: list[RELWarning],
) -> dict[str, Any]:
    """
    Stage 2: construct a candidate attribute-value dict from tokens.

    Returns a dict of {field_name: raw_value}.
    Raises RELFailure(omission) if a required field is absent.
    Appends non-fatal warnings to the warnings list.
    """
    field_map = {f["name"]: f for f in schema["fields"]}
    result: dict[str, Any] = {}

    for key, value in tokens:
        # Normalise key: lowercase, underscores for spaces.
        normalised = key.lower().replace(" ", "_")

        if normalised in result:
            warnings.append(RELWarning(
                failure_type=FailureType.AMBIGUITY_COLLAPSE,
                field=normalised,
                detail=f"Duplicate key '{key}'; using last value.",
            ))

        result[normalised] = value

    # Check required fields.
    for field in schema["fields"]:
        name = field["name"]
        if field.get("required", False) and name not in result:
            raise RELFailure(
                FailureType.OMISSION,
                field=name,
                raw_output=raw,
                detail=f"Required field '{name}' not found in model output",
            )

    # Unknown keys are retained for schema_drift detection in TypeCheck.
    # field_map is currently unused but kept for symmetry and future use.
    _ = field_map

    return result


# ---------------------------------------------------------------------------
# Stage 3: TypeCheck
#
# Enforce schema-level type constraints against Σ.
# For each field in the candidate dict:
#   - If the value is already the declared type, retain it.
#   - If it can be unambiguously coerced, coerce and log the coercion.
#   - If it cannot be coerced and a default exists, use the default and
#     log a misclassification warning (non-fatal).
#   - If it cannot be coerced and no default exists, raise
#     RELFailure(misclassification).
#   - If the field is not in the schema, log schema_drift (non-fatal)
#     and retain the value for the lower stage to handle.
# ---------------------------------------------------------------------------

_TYPE_COERCIONS: dict[str, type] = {
    "float":  float,
    "int":    int,
    "string": str,
}


def typecheck(
    candidate: dict[str, Any],
    schema: dict,
    raw: str,
    warnings: list[RELWarning],
) -> dict[str, Any]:
    """
    Stage 3: enforce schema-level type constraints.

    Returns a type-checked dict. Raises RELFailure(misclassification) if
    a field value cannot be coerced and no default is available.
    """
    field_map = {f["name"]: f for f in schema["fields"]}
    result: dict[str, Any] = {}

    for key, value in candidate.items():
        if key not in field_map:
            warnings.append(RELWarning(
                failure_type=FailureType.SCHEMA_DRIFT,
                field=key,
                detail=(
                    f"Field '{key}' not in SL schema; "
                    f"retained for lower stage"
                ),
            ))
            result[key] = value
            continue

        field_spec = field_map[key]
        declared_type = field_spec.get("type", "string")
        target = _TYPE_COERCIONS.get(declared_type)

        if target is None or isinstance(value, target):
            result[key] = value
            continue

        # Attempt coercion.
        try:
            result[key] = target(value)
            warnings.append(RELWarning(
                failure_type=None,   # not a failure, just a coercion
                field=key,
                detail=(
                    f"Coerced '{key}' from {type(value).__name__} "
                    f"to {declared_type}"
                ),
            ))
        except (ValueError, TypeError):
            default = field_spec.get("default")
            if default is not None:
                result[key] = default
                warnings.append(RELWarning(
                    failure_type=FailureType.MISCLASSIFICATION,
                    field=key,
                    detail=(
                        f"Cannot coerce '{key}' to {declared_type}; "
                        f"using schema default {default!r}"
                    ),
                ))
            else:
                raise RELFailure(
                    FailureType.MISCLASSIFICATION,
                    field=key,
                    raw_output=raw,
                    detail=(
                        f"Cannot coerce '{key}' value {value!r} "
                        f"to {declared_type}; no default available"
                    ),
                )

    return result


# ---------------------------------------------------------------------------
# Stage 4: Lower
#
# Deterministically project the type-checked dict into the SOL canonical
# attribute vocabulary. This stage:
#   - Drops fields not present in the schema vocabulary (schema_drift
#     fields retained through TypeCheck are dropped here).
#   - Applies any field aliases defined in the SL spec.
#   - Attaches provenance metadata to the returned object.
#
# Provenance is attached under "_provenance" and is stripped by downstream
# pipeline operators before invariant checking.
# ---------------------------------------------------------------------------

def lower(
    type_checked: dict[str, Any],
    schema: dict,
    model_version: str = "unknown",
    sl_spec_version: str | None = None,
) -> dict[str, Any]:
    """
    Stage 4: project into SOL canonical attribute vocabulary and attach
    provenance metadata.

    Fields not in the schema vocabulary are silently dropped at this stage —
    they have already been logged as schema_drift in TypeCheck.
    """
    field_names = {f["name"] for f in schema["fields"]}
    aliases: dict[str, str] = {
        f["name"]: f.get("alias", f["name"])
        for f in schema["fields"]
    }

    result: dict[str, Any] = {}

    for key, value in type_checked.items():
        canonical_key = aliases.get(key, key)
        if canonical_key in field_names or key in field_names:
            out_key = aliases.get(key, key)
            result[out_key] = value
        # Fields not in vocabulary are dropped; already logged in TypeCheck.

    result["_provenance"] = {
        "rel_version": REL_VERSION,
        "sl_spec_version": sl_spec_version or schema.get("schema_version", "unknown"),
        "model_version": model_version,
        "extraction_timestamp": time.time(),
        "domain": schema.get("domain", "unknown"),
    }

    return result


def strip_provenance(sol_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Remove provenance metadata from a lowered SOL dict.

    Used by downstream operators that operate purely on the representational
    content and do not need provenance fields.
    """
    return {k: v for k, v in sol_dict.items() if k != "_provenance"}


# ---------------------------------------------------------------------------
# RELCompiler
#
# Composes the four stages into the total mapping REL : Y → R_Σ ∪ {⊥}.
# The compiler is the governed interface between the neural substrate and
# the constitutional pipeline. Its behaviour is fully determined by the
# SL spec; different SL specs produce different compilers over the same
# four-stage architecture.
# ---------------------------------------------------------------------------

@dataclass
class RELCompiler:
    """
    Four-stage deterministic compiler implementing REL : Y → R_Σ ∪ {⊥}.

    Usage
    -----
        compiler = RELCompiler.from_spec("credit_sl_spec.yaml")
        try:
            sol_dict = compiler.compile(raw_text)
        except RELFailure as e:
            trace.record_rel_failure(e.failure_type, e.raw_output, {...})
            sol_dict = None   # ⊥
    """

    schema: dict
    model_version: str = "unknown"

    @classmethod
    def from_spec(cls, spec_path: str, model_version: str = "unknown") -> RELCompiler:
        with open(spec_path, "r") as f:
            schema = yaml.safe_load(f)
        return cls(schema=schema, model_version=model_version)

    def compile(
        self,
        raw: str,
        input_format: str = "text",
    ) -> dict[str, Any]:
        """
        Run all four stages and return the lowered SOL dict.

        Raises RELFailure on any fatal extraction error. Non-fatal
        warnings are available via compile_with_warnings().
        """
        result, _ = self.compile_with_warnings(raw, input_format)
        return result

    def compile_with_warnings(
        self,
        raw: str,
        input_format: str = "text",
    ) -> tuple[dict[str, Any], list[RELWarning]]:
        """
        Run all four stages and return (sol_dict, warnings).

        warnings is a list of non-fatal observation dicts, each containing
        at minimum 'failure_type', 'field', and 'detail' keys. These are
        suitable for inclusion in the trace metadata on a COMMIT entry,
        providing a complete audit record even for clean extractions.

        Raises RELFailure on any fatal extraction error.
        """
        warnings: list[RELWarning] = []

        # Stage 1: Lex
        tokens = lex(raw, input_format)

        # Stage 2: Parse
        candidate = parse(tokens, self.schema, raw, warnings)

        # Stage 3: TypeCheck
        type_checked = typecheck(candidate, self.schema, raw, warnings)

        # Stage 4: Lower
        lowered = lower(
            type_checked,
            self.schema,
            model_version=self.model_version,
            sl_spec_version=self.schema.get("schema_version"),
        )

        return lowered, warnings
