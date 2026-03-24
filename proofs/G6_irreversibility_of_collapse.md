
G6 — Irreversibility of Collapse
1. Statement
Guarantee G6 (Irreversibility of Collapse).
For every constitutional operator f\in O_{\mathrm{const}} and every representation x\in R:
f(\mathrm{Collapse}(x))=x\quad \mathrm{only\  if}\quad x=\mathrm{Canon}(x).
Equivalently:
- No constitutional operator can “undo” a commitment.
- Once a representation has collapsed to its canonical form, the pre‑image cannot be reconstructed unless the input was already canonical.

2. Dependencies
2.1 Definitions
- Collapse:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x)\\ \textstyle x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Canon:
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
- Safe(x) := Inv(x) ∧ NoDrift(x) ∧ WF(x).
- The trace is append‑only by constitutional design (definitional component).
2.2 Axioms
- Axiom 1: Norm(Canon(x)) = Canon(x).
- Axiom 2: ε(Canon(x)) = Canon(x).
- Axiom 3: Sanitize(Canon(x)) = Canon(x).
- Axiom 4: Inv(Sanitize(x)).
- Axiom 5: WF(Sanitize(x)).
2.3 Prior Guarantees
- G3: Safe(Canon(x)).
- G5: Canon(Canon(x)) = Canon(x).
- G4: Collapse(x) = Canon(x) when Safe(x).

3. Lemmas
Lemma 1 — Canon is not injective.
Proof.
Canon is defined as a composition of:
- Norm: may collapse multiple representations to the same fixed point.
- ε: may collapse multiple structures to the same refined form.
- Sanitize: may prune multiple distinct representations to the same invariant‑satisfying subset.
Thus there exist x\neq y such that:
\mathrm{Canon}(x)=\mathrm{Canon}(y).
Therefore Canon has no inverse in O_{\mathrm{const}}.
□

Lemma 2 — Collapse returns Canon(x) whenever Safe(x).
From G3:
\mathrm{Safe}(\mathrm{Canon}(x)).
Thus:
\mathrm{Collapse}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
And for any safe x:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
□

Lemma 3 — No constitutional operator can reconstruct a pre‑canonical form.
Proof.
Let y=\mathrm{Canon}(x).
By Lemma 1, Canon is not injective.
Thus there is no function f\in O_{\mathrm{const}} such that:
f(y)=x
for all x in the pre‑image of y.
Since O_{\mathrm{const}} contains only:
- Norm
- ε
- Sanitize
- Canon
- Collapse
- compositions thereof
and all of these operators either:
- leave canonical forms unchanged (Axioms 1–3), or
- map to canonical forms (Canon, Collapse),
none can reconstruct a non‑canonical pre‑image.
□

4. Full Proof of G6
We must show:
\forall f\in O_{\mathrm{const}}:\; f(\mathrm{Collapse}(x))=x\Rightarrow x=\mathrm{Canon}(x).

Step 1 — Consider the output of Collapse
There are two cases.
Case 1 — Safe(x)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
Assume:
f(\mathrm{Canon}(x))=x.
But by Lemma 3, no constitutional operator can reconstruct a non‑canonical pre‑image from a canonical form.
Thus:
x=\mathrm{Canon}(x).

Case 2 — ¬Safe(x)
Then:
\mathrm{Collapse}(x)=x.
Assume:
f(x)=x.
This is possible only if x is already a fixed point of all constitutional operators.
But the only fixed points of all operators in O_{\mathrm{const}} are canonical forms (Axioms 1–3).
Thus:
x=\mathrm{Canon}(x).

Step 2 — No operator can undo canonicalization
From Lemma 3:
\forall y\in \mathrm{Canon}(R),\; \forall f\in O_{\mathrm{const}}:\; f(y)=y.
Thus:
f(\mathrm{Collapse}(x))=x\Rightarrow x=\mathrm{Canon}(x).

5. Conclusion
Collapse is irreversible:
- Once a representation has collapsed to its canonical form, no constitutional operator can reconstruct any non‑canonical predecessor.
- The only representations that can be recovered from Collapse(x) are those that were already canonical.
- This follows from the fixed‑point axioms and the non‑injectivity of Canon.
Thus:
f(\mathrm{Collapse}(x))=x\quad \Rightarrow \quad x=\mathrm{Canon}(x).
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G6: Irreversibility of Collapse
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


