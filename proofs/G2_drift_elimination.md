
G2 — Drift Elimination
1. Statement
Guarantee G2 (Drift Elimination).
For every representation x\in R:
\mathrm{NoDrift}(\mathrm{Canon}(x)).
Where:

That is, the canonical form of any representation is always a fixed point of the normalization operator.

2. Dependencies
2.1 Definitions
- R: finite representational space of SOL objects (A1).
- \mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
- \mathrm{NoDrift}(y):=(\mathrm{Norm}(y)=y).
- BR: canonical basis of the representational space (implicit in A2).
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).- Axiom A2 (Convergent Normalization).
Norm converges to a fixed point under finite iteration.
2.3 Operator Structure
- Norm: drift‑eliminating contraction (or finite‑iteration convergent operator).
- ε: structural refinement.
- Sanitize: invariant‑restoring pruning.
- Canon: composition of the above.

3. Lemmas
Lemma 1 — Norm has fixed points for all inputs.
From A2 (finite‑iteration convergence):
For every x\in R, there exists k<|R| such that:

and

Thus every representation has a drift‑free limit point.
□

Lemma 2 — Canon(x) is a fixed point of Norm.
Proof.
By Axiom 1:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus Canon(x) is itself a fixed point of Norm.
□

Lemma 3 — ε and Sanitize do not reintroduce drift.
Proof.
For any canonical y=\mathrm{Canon}(x):
- Axiom 2: \varepsilon (y)=y.
- Axiom 3: \mathrm{Sanitize}(y)=y.
Thus neither operator modifies canonical forms, and therefore neither can introduce attributes requiring further normalization.
□

4. Full Proof of G2
We must show:
\forall x\in R:\; \mathrm{NoDrift}(\mathrm{Canon}(x)).
Expanding the definition:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
This is exactly Axiom 1.
But to present the full formal reasoning (Style A), we proceed structurally.

Step 1 — Norm converges to a fixed point for any input
By Lemma 1, for any x\in R, repeated application of Norm yields a fixed point  such that:

Thus drift can always be eliminated.

Step 2 — Canon(x) is constructed from the converged form
Canon(x) is defined as:
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
Since Norm(x) converges to a fixed point , and ε and Sanitize are deterministic and total, Canon(x) is a deterministic function of .

Step 3 — Canon(x) is itself a fixed point of Norm
By Axiom 1:
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
Thus:
\mathrm{NoDrift}(\mathrm{Canon}(x)).

Step 4 — ε and Sanitize cannot reintroduce drift
By Lemma 3:
- ε leaves canonical forms unchanged.
- Sanitize leaves canonical forms unchanged.
Thus no operator in the canonical pipeline can produce a representation requiring further normalization.

Step 5 — Conclusion
Combining Steps 1–4:
\forall x\in R:\; \mathrm{NoDrift}(\mathrm{Canon}(x)).
Thus the canonical form of any representation is drift‑free.
□

5. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G2: Drift Elimination
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


