# Governed Representational Chain — Minimal Demonstration

This repository demonstrates the governed representational chain described in the paper Constitutional Governance by Design. It implements a minimal SL → REL → SOL → Canonical Output pipeline, showing how structured safety constraints can be enforced deterministically. The architecture guarantees soundness and converts unknown safety failures into visible specification failures. This repo is designed for clarity, auditability, and reviewer inspection.

Component Overview

SL (Specification Language)

- sl_spec.yaml: Defines extraction rules, types, and requirements. Governs how raw text is interpreted.
REL (Representation Extraction Layer)
- rel_interpreter.py: Loads the SL spec and deterministically extracts typed fields from raw text. No heuristics or model inference.
SOL (Substrate Object Language)
- sol.py: Defines structured, validated TaskSOL objects. Every committed state is inspectable and enforceable.
Canonicalization Pipeline
- canonicalize.py: Applies Canon(x) := Sanitize(Enforce(Norm(x))) to produce the final governed output.
Verification and Demo
- test_pipeline.py: End-to-end test confirming the representational chain.
- run_example.py: Minimal demonstration of the full pipeline.

This repository provides a minimal, fully inspectable example of the
governed representational chain described in the paper:

How to Run

To verify the representational chain:
python run_example.py

To run the end-to-end test:
python -c "from test_pipeline import test_end_to_end_pipeline; test_end_to_end_pipeline()"

Expected output:
{
  "task": "Write the introduction",
  "priority": "high"
}

The test will confirm that the SL → REL → SOL → Canonical Output pipeline is functioning correctly. All components integrate deterministically, with no heuristics or model inference.


**SL → REL → SOL → Canonical Output**

The goal is not to provide a production system, but a tiny, runnable,
auditable demonstration of the architecture.

---

## Components

### 1. SL (Specification Language)
`sl_spec.yaml` defines a small set of extraction rules, types, and
requirements. It governs how raw text is interpreted.

### 2. REL (Representation Extraction Layer)
`rel_interpreter.py` loads the SL spec and deterministically extracts
typed fields from raw text. No heuristics or model inference are used.

### 3. SOL (Substrate Object Layer)
`sol.py` defines a finite, typed, invariant-checked object that
represents the constitutional substrate.

### 4. Example Run
`run_example.py` executes the full pipeline:


raw text → REL dict → SOL object → canonical JSON

---

## Running the Example


python run_example.py

You should see:

```json
{
  "task": "Write the introduction",
  "priority": "high"
}



Diagram
flowchart TD
    A[Raw Text] -->|governed by SL| B[REL Extraction]
    B -->|validated into SOL| C[SOL Object]
    C -->|canonicalization| D[Canonical Output]

This schematic illustrates the governed representational chain: raw input is interpreted via SL rules, extracted deterministically by REL, validated into structured SOL objects, and canonicalized into enforceable output. Each stage is inspectable, auditable, and governed.

Tests
A single test (test_pipeline.py) verifies the entire governed chain end-to-end.


