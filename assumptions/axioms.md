
Axioms of the Canonical Pipeline
These five axioms define the constitutional behavior of the canonical pipeline (Norm → ε → Sanitize). They are the foundational laws from which all ten constitutional guarantees are derived. Each axiom is operational, total, and implementation‑independent. Totality ensures that the canonical pipeline never fails silently; every input has a defined canonical outcome.

These axioms constrain the behavior of any compliant implementation of the canonical pipeline. They are not empirical claims but definitional requirements.

Axiom 1 — Norm Fixed Point
For all representations x\in R:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Meaning.
Normalization eliminates representational drift and has no effect on canonical forms.

Axiom 2 — Refinement Fixed Point
For all representations x\in R:
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
Meaning.
Structural refinement cannot modify a canonical form.

Axiom 3 — Sanitize Fixed Point
For all representations x\in R:
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Meaning.
Sanitize is idempotent on canonical forms and cannot prune or alter them.

Axiom 4 — Sanitize Restores Invariants
For all representations x \in \mathbb{R} \cup \{\bot\}:
\mathrm{Inv}(\mathrm{Sanitize}(x)).
Meaning.
Sanitize always returns an invariant‑satisfying representation, regardless of input ($\bot$ vacuously satisfies $\mathit{Inv}$ and $\mathit{WF}$ by convention).

Axiom 5 — Sanitize Enforces Well‑Formedness
For all representations x \in \mathbb{R} \cup \{\bot\}:
\mathrm{WF}(\mathrm{Sanitize}(x)).
Meaning.
Sanitize ensures schema compliance; malformed structures cannot survive the final stage of the pipeline.

Canonical Pipeline Definition
For reference:
\mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
These axioms collectively ensure that Canon is a projection onto the constitutional subspace and that Collapse is deterministic, safe, and irreversible.
