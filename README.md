# Governed Representational Chain — Minimal Demonstration

This repository provides a minimal, fully inspectable example of the
governed representational chain described in the paper:

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



Tests
A single test (test_pipeline.py) verifies the entire governed chain end-to-end.
