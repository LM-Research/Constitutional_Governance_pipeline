
G3 — Pipeline Safety
1. Statement
Guarantee G3 (Pipeline Safety).
For every representation x\in R:
\mathrm{Safe}(\mathrm{Canon}(x)),
where:
\mathrm{Safe}(y):=\mathrm{Inv}(y)\; \wedge \; \mathrm{NoDrift}(y)\; \wedge \; \mathrm{WF}(y).
That is, the canonical form of any representation is always:
- invariant‑satisfying
- drift‑free
- well‑formed
simultaneously.

2. Dependencies
2.1 Definitions
- R: finite representational space (A1).
- \mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
- \mathrm{Inv}(y): conjunction of decidable invariants (A5).
- \mathrm{NoDrift}(y):=(\mathrm{Norm}(y)=y).
- \mathrm{WF}(y): well‑formedness under schema \Sigma .
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4 (Sanitize Restores Invariants).
\mathrm{Inv}(\mathrm{Sanitize}(y)) for all y\in R.
- Axiom 5 (Sanitize Enforces Well‑Formedness).
\mathrm{WF}(\mathrm{Sanitize}(y)) for all y\in R.
2.3 Prior Guarantees
- G2 (Drift Elimination).
\mathrm{NoDrift}(\mathrm{Canon}(x)).

3. Lemmas
Lemma 1 — Canon(x) satisfies Inv.
Proof.
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
By Axiom 4:
\mathrm{Inv}(\mathrm{Sanitize}(y))\quad \forall y.
Thus:
\mathrm{Inv}(\mathrm{Canon}(x)).
□

Lemma 2 — Canon(x) satisfies NoDrift.
This is exactly G2, already proven:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{NoDrift}(\mathrm{Canon}(x)).
□

Lemma 3 — Canon(x) satisfies WF.
Proof.
By Axiom 5:
\mathrm{WF}(\mathrm{Sanitize}(y))\quad \forall y.
Since Canon(x) ends with Sanitize:
\mathrm{WF}(\mathrm{Canon}(x)).
□

4. Full Proof of G3
We must show:
\forall x\in R:\; \mathrm{Safe}(\mathrm{Canon}(x)).
Expanding Safe:
\mathrm{Inv}(\mathrm{Canon}(x))\; \wedge \; \mathrm{NoDrift}(\mathrm{Canon}(x))\; \wedge \; \mathrm{WF}(\mathrm{Canon}(x)).
We prove each conjunct.

Step 1 — Invariant Satisfaction
By Lemma 1:
\mathrm{Inv}(\mathrm{Canon}(x)).
This follows from Axiom 4 applied to the final Sanitize step.

Step 2 — Drift‑Freedom
By Lemma 2 (G2):
\mathrm{NoDrift}(\mathrm{Canon}(x)).
This follows from Axiom 1 (Norm fixed point).

Step 3 — Well‑Formedness
By Lemma 3:
\mathrm{WF}(\mathrm{Canon}(x)).
This follows from Axiom 5 (Sanitize enforces WF).

Step 4 — Conjunction
Since all three properties hold independently:
\mathrm{Safe}(\mathrm{Canon}(x)).
Thus the canonical pipeline always produces a representation satisfying all safety conditions simultaneously.
□

5. Interpretation
This is the central safety theorem of the architecture:
- No unsafe representation can survive canonicalization.
- No malformed representation can survive canonicalization.
- No drifting or unstable representation can survive canonicalization.
The canonical pipeline is therefore a structural safety mechanism, not a statistical one.

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G3: Pipeline Safety
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


