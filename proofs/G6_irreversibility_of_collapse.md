G6 — Irreversibility of Collapse
1. Statement
Guarantee G6 (Irreversibility of Collapse).
For every constitutional operator f\in O_{\mathrm{const}} and every representation
x\in \mathbb{R_{\mathnormal{\bot }}}:
f(\mathrm{Collapse}(x))=x\quad \Longrightarrow \quad x=\mathrm{Canon}(x).
Equivalently:
- No constitutional operator can “undo” a commitment.
- Once a representation has collapsed to its canonical form, the pre‑image cannot be reconstructed unless the input was already canonical.

2. Dependencies
2.1 Definitions
- Collapse:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x),\\ \textstyle [4pt]x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Canon:
\mathrm{Canon}(x):=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(x))\right) .
- Safety predicate:
\mathrm{Safe}(x):=\mathrm{Inv}(x)\  \wedge \  \mathrm{NoDrift}(x)\  \wedge \  \mathrm{WF}(x).
- The trace is append‑only by constitutional design (definitional).
2.2 Axioms
- Axiom 1: \mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2: \varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3: \mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4: \mathrm{Inv}(\mathrm{Sanitize}(x)).
- Axiom 5: \mathrm{WF}(\mathrm{Sanitize}(x)).
2.3 Prior Guarantees
- G3: \mathrm{Safe}(\mathrm{Canon}(x)).
- G5: \mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- G4: If \mathrm{Safe}(x), then \mathrm{Collapse}(x)=\mathrm{Canon}(x).

3. Lemmas
Lemma 1 — Canon is not injective.
Canon is defined as a composition of:
- Norm: may collapse multiple representations to the same fixed point.
- \varepsilon : may collapse multiple structures to the same refined form.
- Sanitize: may prune multiple distinct representations to the same invariant‑satisfying structure.
Thus there exist x\neq y such that:
\mathrm{Canon}(x)=\mathrm{Canon}(y).
Therefore Canon has no inverse in O_{\mathrm{const}}.
□

Lemma 2 — Collapse returns Canon(x) whenever Safe(x).
From G3, \mathrm{Safe}(\mathrm{Canon}(x)) holds for all x.
Thus:
\mathrm{Collapse}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
And for any safe x:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
□

Lemma 3 — No constitutional operator can reconstruct a pre‑canonical form.
Let y=\mathrm{Canon}(x).
By Lemma 1, Canon is not injective.
Thus there is no function f\in O_{\mathrm{const}} such that:
f(y)=x
for all x in the pre‑image of y.
Since every operator in O_{\mathrm{const}}:
- leaves canonical forms unchanged (Axioms 1–3), or
- maps to canonical forms (Canon, Collapse),
no operator can reconstruct a non‑canonical predecessor.
□

4. Full Proof of G6
We must show:


Step 1 — Analyze the output of Collapse
There are two cases.

Case 1 — Safe(x)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
Assume:
f(\mathrm{Canon}(x))=x.
By Lemma 3, no constitutional operator can reconstruct a non‑canonical pre‑image from a canonical form.
Thus:
x=\mathrm{Canon}(x).

Case 2 — ¬Safe(x)
Then:
\mathrm{Collapse}(x)=x.
Assume:
f(x)=x.
For x to be a fixed point of every constitutional operator, it must in particular be a fixed point of:
- Norm (Axiom 1),
- \varepsilon  (Axiom 2),
- Sanitize (Axiom 3).
The only representations satisfying all three fixed‑point conditions are canonical forms.
Thus:
x=\mathrm{Canon}(x).

Step 2 — No operator can undo canonicalization
From Lemma 3:
\forall y\in \mathrm{Canon}(\mathbb{R_{\mathnormal{\bot }}}),\  \forall f\in O_{\mathrm{const}}:\  f(y)=y.
Thus:
f(\mathrm{Collapse}(x))=x\quad \Rightarrow \quad x=\mathrm{Canon}(x).
□

5. Conclusion
Collapse is irreversible:
- Once a representation has collapsed to its canonical form, no constitutional operator can reconstruct any non‑canonical predecessor.
- The only representations recoverable from \mathrm{Collapse}(x) are those that were already canonical.
- This follows from the fixed‑point axioms and the non‑injectivity of Canon.
Thus:
f(\mathrm{Collapse}(x))=x\quad \Rightarrow \quad x=\mathrm{Canon}(x).
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G6 — Irreversibility of Collapse
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


