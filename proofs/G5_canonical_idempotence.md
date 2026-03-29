G5 — Canonical Idempotence
1. Statement
Guarantee G5 (Canonical Idempotence).
For every representation x\in \mathbb{R_{\mathnormal{\bot }}}:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
That is, canonicalization is idempotent: once a representation has been canonicalized, re‑canonicalizing it produces no further change.

2. Dependencies
2.1 Definitions
- Canonical pipeline:
\mathrm{Canon}(x):=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(x))\right) .
- Norm: normalization operator.
- \varepsilon : structural refinement operator.
- Sanitize: invariant‑restoring pruning operator.
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Together, these axioms assert that every stage of the canonical pipeline is a fixed point on canonical forms.

3. Lemmas
Lemma 1 — Norm leaves canonical forms unchanged.
Immediate from Axiom 1:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

Lemma 2 — \varepsilon  leaves canonical forms unchanged.
Immediate from Axiom 2:
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

Lemma 3 — Sanitize leaves canonical forms unchanged.
Immediate from Axiom 3:
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

4. Full Proof of G5
We must show:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Start with the definition:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(\mathrm{Canon}(x)))\right) .
We apply the fixed‑point axioms step by step.

Step 1 — Apply Axiom 1 (Norm fixed point)
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Canon}(x))\right) .

Step 2 — Apply Axiom 2 (Refinement fixed point)
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Sanitize}(\mathrm{Canon}(x)).

Step 3 — Apply Axiom 3 (Sanitize fixed point)
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

5. Conclusion
Canonicalization is idempotent:
- Norm does not modify canonical forms.
- \varepsilon  does not modify canonical forms.
- Sanitize does not modify canonical forms.
Therefore, the entire canonical pipeline is a projection operator onto the constitutional subspace:
\mathrm{Canon}\circ \mathrm{Canon}=\mathrm{Canon}.
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G5 — Canonical Idempotence
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


