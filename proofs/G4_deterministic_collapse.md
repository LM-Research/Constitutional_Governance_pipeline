G4 — Deterministic Collapse
1. Statement
Guarantee G4 (Deterministic Collapse).
For all representations x,y\in \mathbb{R_{\mathnormal{\bot }}}:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\quad \Longleftrightarrow \quad \mathrm{Canon}(x)=\mathrm{Canon}(y).
That is, Collapse is deterministic, and two representations collapse to the same committed state if and only if their canonical forms are identical.

2. Dependencies
2.1 Definitions
- Canonical pipeline:
\mathrm{Canon}(x):=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(x))\right) .
- Collapse:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x),\\ \textstyle [4pt]x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Safety predicate:
\mathrm{Safe}(x):=\mathrm{Inv}(x)\  \wedge \  \mathrm{NoDrift}(x)\  \wedge \  \mathrm{WF}(x).
- From G3:
\mathrm{Safe}(\mathrm{Canon}(x)) holds for all x.
2.2 Axioms
- Axiom 1: \mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2: \varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3: \mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4: \mathrm{Inv}(\mathrm{Sanitize}(x)).
- Axiom 5: \mathrm{WF}(\mathrm{Sanitize}(x)).
2.3 Prior Guarantees
- G3: \mathrm{Safe}(\mathrm{Canon}(x)) for all x.
- G5 (implicit): Canon is idempotent:
\mathrm{Canon}(\mathrm{Canon}(x))=\mathrm{Canon}(x).

3. Lemmas
Lemma 1 — Collapse returns Canon(x) on canonical input.
From G3, \mathrm{Safe}(\mathrm{Canon}(x)) holds for all x.
Thus:
\mathrm{Collapse}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

Lemma 2 — Canon is total.
Canon is a composition of total operators:
- Norm: total (A1, A2)
- \varepsilon : total
- Sanitize: total
Thus:
\forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{Canon}(x)\  \mathrm{is\  defined}.
□

Lemma 3 — Collapse is deterministic.
Collapse is defined by a deterministic case distinction:
- If \mathrm{Safe}(x), return \mathrm{Canon}(x).
- Otherwise return x.
Since Safe is decidable and Canon is deterministic (Lemma 2), Collapse is deterministic.
□

4. Full Proof of G4
We must show:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\quad \Longleftrightarrow \quad \mathrm{Canon}(x)=\mathrm{Canon}(y).
We prove both directions.

(⇒) Forward Direction
Assume:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).
We analyze cases based on the definition of Collapse.

Case 1 — Safe(x) and Safe(y)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x),\quad \mathrm{Collapse}(y)=\mathrm{Canon}(y).
Thus:
\mathrm{Canon}(x)=\mathrm{Canon}(y).

Case 2 — Safe(x) and ¬Safe(y)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x),\quad \mathrm{Collapse}(y)=y.
Equality implies:
\mathrm{Canon}(x)=y.
But y is unsafe, while \mathrm{Canon}(x) is always safe (G3).
Contradiction.
Thus this case is impossible.

Case 3 — ¬Safe(x) and Safe(y)
Symmetric to Case 2.
Also impossible.

Case 4 — ¬Safe(x) and ¬Safe(y)
Then:
\mathrm{Collapse}(x)=x,\quad \mathrm{Collapse}(y)=y.
Equality implies:
x=y.
Since Canon is a function (Lemma 2):
\mathrm{Canon}(x)=\mathrm{Canon}(y).

Conclusion of Forward Direction

□

(⇐) Reverse Direction
Assume:
\mathrm{Canon}(x)=\mathrm{Canon}(y).
We must show:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).

Case 1 — Safe(x)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
Since \mathrm{Canon}(x)=\mathrm{Canon}(y):
\mathrm{Collapse}(x)=\mathrm{Canon}(y).
If Safe(y), then Collapse(y) = Canon(y).
If ¬Safe(y), then Collapse(y) = y, but:
y=\mathrm{Canon}(y)
would imply y is canonical and therefore safe — contradiction.
Thus Safe(y) must hold.
Therefore:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).

Case 2 — ¬Safe(x)
Then:
\mathrm{Collapse}(x)=x.
If Safe(y), then Collapse(y) = Canon(y), which cannot equal x unless x=\mathrm{Canon}(y), contradicting ¬Safe(x).
Thus y is also unsafe.
So:
\mathrm{Collapse}(x)=x=y=\mathrm{Collapse}(y).

Conclusion of Reverse Direction

□

5. Final Conclusion
Combining both directions:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\quad \Longleftrightarrow \quad \mathrm{Canon}(x)=\mathrm{Canon}(y).
Thus Collapse is deterministic, reproducible, and induces the same equivalence relation as canonicalization.
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G4 — Deterministic Collapse
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


