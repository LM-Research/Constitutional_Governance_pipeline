# Governed Representational Chain — Minimal Reference Implementation

This repository provides a minimal, fully inspectable implementation of the
governed representational chain described in the paper:

> **Constitutional Governance by Design: A Formal Architecture for Safe,
> Auditable AI** — Lucas Mansell

The pipeline implements the full governed chain:

```
SL spec → REL extraction → SOL object → Canonical output
```

The goal is not a production system. It is a small, deterministic,
auditable demonstration of the architecture: every stage is labelled,
every failure mode is typed, and the full pipeline can be read and
verified by a non-specialist in a single sitting.

---

## Components

### `sl_spec.yaml` — Specification Language

Defines extraction rules, field types, required/optional status, and
default values. Governs how raw model output is interpreted by the REL.

### `rel_interpreter.py` — Representation Extraction Layer (REL)

Loads the SL spec and deterministically extracts typed fields from raw
text. No heuristics or model inference are used. Raises a typed
`SpecViolation` if a required field is absent.

### `sol.py` — Substrate Object Layer (SOL)

Defines a finite, typed, invariant-checked object. Construction fails
with a `ValueError` if the priority field is not a member of the
permitted enum. No object violating the schema can enter the canonical
pipeline.

### `run_example.py` — End-to-end demonstration

Runs four scenarios through the full governed chain:

- **Example 1**: Well-formed input → canonical JSON output
- **Example 2**: Missing optional field → default applied by REL
- **Example 3**: Missing required field → `SpecViolation` raised, pipeline halts
- **Example 4**: Invalid enum value → `ValueError` raised by SOL layer

Each failure mode is typed and surfaced explicitly. Nothing fails silently.

### `test_pipeline.py` — End-to-end test

Verifies the full governed chain for a well-formed input using `pytest`.

---

## Running the demonstration

```bash
python run_example.py
```

## Running the tests

```bash
pytest test_pipeline.py
```

---

## Pipeline diagram

```
flowchart TD
    A[Raw Model Output] -->|governed by SL| B[REL Extraction]
    B -->|SpecViolation if required field absent| E[Halt]
    B -->|typed fields| C[SOL Object]
    C -->|ValueError if invariant violated| E
    C -->|canonical| D[Canonical JSON Output]
```

---

## Dependencies

- Python 3.8+
- `pyyaml` (`pip install pyyaml`)

---

## License

MIT
