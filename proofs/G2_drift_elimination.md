G2 — Drift Elimination
1. Statement
Guarantee G2 (Drift Elimination).
For every representation x\in \mathbb{R_{\mathnormal{\bot }}}:
\mathrm{NoDrift}(\mathrm{Canon}(x)).
Where:
\mathrm{NoDrift}(y):=(\mathrm{Norm}(y)=y).
That is, the canonical form of any representation is always a fixed point of the normalization operator.

2. Dependencies
2.1 Definitions
- \mathbb{R}: finite or finitely branching representational space (A1).
- Canonical pipeline:
\mathrm{Canon}(x):=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(x))\right) .
- Drift predicate:
\mathrm{NoDrift}(y):=(\mathrm{Norm}(y)=y).
- Convergent normalization (A2):
repeated application of Norm reaches a fixed point.
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Assumption A2 (Convergent Normalization).
Norm converges to a fixed point under finite iteration.
2.3 Operator Structure
- Norm: drift‑eliminating contraction.
- \varepsilon : structural refinement.
- Sanitize: invariant‑restoring pruning.
- Canon: composition of the above.

3. Lemmas
Lemma 1 — Norm has fixed points for all inputs.
From A2 (finite‑iteration convergence):
\forall x\in \mathbb{R_{\mathnormal{\bot }}},\  \exists k\in \mathbb{N}:\  \mathrm{Norm^{\mathnormal{k}}}(x)=\mathrm{Norm^{\mathnormal{k+1}}}(x).
Thus every representation has a drift‑free limit point.
□

Lemma 2 — Canon(x) is a fixed point of Norm.
From Axiom 1:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus Canon(x) is itself drift‑free.
□

Lemma 3 — \varepsilon  and Sanitize do not reintroduce drift.
For any canonical y=\mathrm{Canon}(x):
- Axiom 2: \varepsilon (y)=y.
- Axiom 3: \mathrm{Sanitize}(y)=y.
Thus neither operator modifies canonical forms, and therefore neither can introduce drift.
□

4. Full Proof of G2
We must show:
\forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{NoDrift}(\mathrm{Canon}(x)).
Expanding the definition:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
This is exactly Axiom 1.
However, we present the full structural reasoning for completeness.

Step 1 — Norm converges to a fixed point
By Lemma 1, for any x, repeated application of Norm yields a fixed point  such that:

Thus drift can always be eliminated.

Step 2 — Canon(x) is constructed from the converged form
Canon is defined as:
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
Since Norm converges and both \varepsilon  and Sanitize are total and deterministic, Canon(x) is a deterministic function of the drift‑free limit.

Step 3 — Canon(x) is itself drift‑free
By Axiom 1:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{NoDrift}(\mathrm{Canon}(x)).

Step 4 — \varepsilon  and Sanitize cannot reintroduce drift
By Lemma 3:
- \varepsilon  leaves canonical forms unchanged.
- Sanitize leaves canonical forms unchanged.
Thus no operator in the canonical pipeline can produce a representation requiring further normalization.

Step 5 — Conclusion
Combining Steps 1–4:
\forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{NoDrift}(\mathrm{Canon}(x)).
Thus the canonical form of any representation is drift‑free.
□

5. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G2 — Drift Elimination
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


