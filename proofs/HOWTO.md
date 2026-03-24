
How to Work With the Constitutional Proof Corpus
This guide explains how to read the proofs, how to extend them, and how to mechanize them in a formal verification environment.

1. How to Read the Proofs
Each proof file follows the same structure:
- Statement
The formal guarantee being proven.
- Dependencies
Axioms, definitions, and assumptions required for the proof.
- Lemmas
Small, reusable results that isolate the key reasoning steps.
- Full Proof
A structured derivation in classical formal‑methods style.
- Interpretation
A short explanation of the operational meaning.
- Cross‑References
Links to the paper and assumptions.
Recommended Reading Order
- Start with G3 (Pipeline Safety) — the central theorem.
- Then read G1, G2, G5 — the algebraic foundation.
- Then G4, G6, G7 — commitment and trace guarantees.
- Finally G8–G10 — distributed guarantees.

2. How to Extend the Proof Corpus
When adding new guarantees or invariants:
Step 1 — Add new assumptions or invariants
Place them in /assumptions and keep them minimal.
Step 2 — Add new lemmas
If a lemma is reused across multiple guarantees, place it in a shared file (e.g., lemmas.md).
Step 3 — Add a new proof file
Follow the existing structure:
G11_new_property.md


Step 4 — Update the dependency diagram
Add new edges only where necessary.
Step 5 — Keep the style consistent
- No prose proofs
- No informal reasoning
- Use explicit operator algebra and fixed‑point arguments
- Reference axioms by number

3. How to Mechanize These Proofs
The corpus is intentionally structured to support mechanization in:
- Coq
- Isabelle/HOL
- Lean
- TLA+ (for temporal and distributed guarantees)
Mechanization Strategy
- Define the representational space
As a finite or finitely branching type.
- Encode the operators
Norm, ε, Sanitize, Canon, Collapse as total functions.
- Encode the axioms
As lemmas or rewrite rules.
- Encode the safety predicates
Inv, WF, NoDrift as decidable predicates.
- Prove the guarantees
Using the same lemma structure as the Markdown proofs.
Recommended Order for Mechanization
- G5 (Idempotence)
- G1 (Invariant Preservation)
- G2 (Drift Elimination)
- G3 (Pipeline Safety)
- G4 (Deterministic Collapse)
- G6–G10
This order minimizes dependency complexity.
