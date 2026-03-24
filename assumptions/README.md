
Assumptions and Axioms
This directory contains the axiomatic foundation and structural assumptions that underlie the canonical pipeline and the ten constitutional guarantees. These files define the mathematical substrate of the architecture and serve as the normative reference for all proofs in /proofs.

Files
axioms.md
structural_assumptions.md


axioms.md
Defines the five axioms governing the canonical pipeline:
- Norm fixed point
- Refinement fixed point
- Sanitize fixed point
- Sanitize restores invariants
- Sanitize enforces well‑formedness
These axioms are the core laws of the constitutional substrate.
structural_assumptions.md
Specifies the structural properties of the representational space:
- finiteness / finite branching
- convergent normalization
- totality of operators
- decidability of safety predicates
- invariant decomposition
- distributed communication assumptions
These assumptions ensure that the canonical pipeline is well‑defined, terminating, and compositional.

Relationship to the Proof Corpus
All proofs in /proofs explicitly reference:
- the axioms in axioms.md
- the structural assumptions in structural_assumptions.md
This directory is therefore the root of the formal dependency graph for the entire architecture.

Philosophy
The assumptions and axioms are:
- minimal — no unnecessary constraints
- domain‑agnostic — applicable to any representational substrate
- mechanizable — suitable for future Coq/Isabelle/TLA+ formalization
- auditable — clear enough for regulatory review
They define the constitutional “physics” of the system.

If you want, I can now generate:
- a top‑level repo README
- a dependency diagram showing how axioms → lemmas → guarantees connect
- a How to mechanize these proofs guide
- or a glossary for the repo
Just tell me where you want to go next.
