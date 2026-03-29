How to Work With the Constitutional Proof Corpus
This guide explains how to read the proofs, how to extend the corpus, and how to mechanize the guarantees in a formal verification environment. It is intended for reviewers, contributors, and engineers implementing the architecture in proof assistants.

1. How to Read the Proofs
Each proof file follows a uniform structure:
• Statement
The formal guarantee being proven.
• Dependencies
Axioms, definitions, assumptions, and prior guarantees required for the proof.
• Lemmas
Small, reusable results that isolate the key reasoning steps.
• Full Proof
A structured derivation in classical formal‑methods style, using operator algebra, fixed‑point reasoning, and explicit case analysis.
• Interpretation
A short explanation of the operational meaning of the guarantee.
• Cross‑References
Pointers to the paper, axioms, structural assumptions, and related guarantees.

Recommended Reading Order
To understand the architecture efficiently:
- Start with G3 (Pipeline Safety)
The central theorem; all other guarantees depend on it.
- Then read G1, G2, G5
The algebraic foundation: invariant preservation, drift elimination, idempotence.
- Then G4, G6, G7
Commitment, irreversibility, and trace guarantees.
- Finally G8–G10
The distributed guarantees: safety, agreement, and closure.
This order mirrors the dependency graph and minimizes cognitive load.

2. How to Extend the Proof Corpus
When adding new guarantees, invariants, or operators, follow this workflow:

Step 1 — Add New Assumptions or Invariants
Place new assumptions in /assumptions/.
Keep them:
- minimal (no unnecessary constraints)
- domain‑agnostic
- mechanizable
- auditable
If adding new invariants, define them as decidable predicates and document their decomposition.

Step 2 — Add New Lemmas
If a lemma is reused across multiple guarantees, place it in a shared file such as:
/proofs/lemmas.md


Keep lemmas small, composable, and explicitly tied to axioms.

Step 3 — Add a New Proof File
Follow the existing structure:
G11_new_property.md


Use the same section headings:
- Statement
- Dependencies
- Lemmas
- Full Proof
- Interpretation
- Cross‑References
Avoid prose proofs; use explicit operator algebra and fixed‑point reasoning.

Step 4 — Update the Dependency Diagram
Modify /proofs/dependencies.md:
- Add new nodes only where necessary
- Add edges only when the new guarantee depends on an existing one
- Keep the diagram minimal and readable

Step 5 — Maintain Style Consistency
- No informal reasoning
- No hidden steps
- Reference axioms by number
- Use the same LaTeX conventions
- Keep proofs modular and compositional
This ensures the corpus remains uniform and mechanizable.

3. How to Mechanize These Proofs
The corpus is intentionally structured to support mechanization in:
- Coq
- Isabelle/HOL
- Lean
- TLA+ (for temporal and distributed guarantees)

Mechanization Strategy
1. Define the Representational Space
Model \mathbb{R} as a finite or finitely branching type (A1).
2. Encode the Operators
Define:
- Norm
- ε
- Sanitize
- Canon
- Collapse
as total functions \mathbb{R_{\mathnormal{\bot }}}\rightarrow \mathbb{R_{\mathnormal{\bot }}}.
3. Encode the Axioms
Represent Axioms 1–5 as:
- rewrite rules
- lemmas
- invariants
- fixed‑point theorems
depending on the proof assistant.
4. Encode the Safety Predicates
Define:
- Inv
- WF
- NoDrift
as decidable predicates.
5. Prove the Guarantees
Follow the same structure as the Markdown proofs:
- prove lemmas first
- then prove each guarantee
- use the dependency graph to minimize complexity

Recommended Order for Mechanization
To minimize dependency depth:
- G5 — Canonical Idempotence
- G1 — Invariant Preservation
- G2 — Drift Elimination
- G3 — Pipeline Safety
- G4 — Deterministic Collapse
- G6–G10 — Commitment, Trace, and Distributed Guarantees
This order mirrors the algebraic buildup of the architecture.
