
G4 — Deterministic Collapse
1. Statement
Guarantee G4 (Deterministic Collapse).
For all representations x,y\in R:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\; \; \Longleftrightarrow \; \; \mathrm{Canon}(x)=\mathrm{Canon}(y).
That is, Collapse is deterministic and two representations collapse to the same committed state if and only if their canonical forms are identical.

2. Dependencies
2.1 Definitions
- \mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
- Collapse is defined as:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x)\\ \textstyle x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Safe(x) := Inv(x) ∧ NoDrift(x) ∧ WF(x).
- From G3, Safe(Canon(x)) holds for all x.
2.2 Axioms
- Axiom 1: Norm(Canon(x)) = Canon(x).
- Axiom 2: ε(Canon(x)) = Canon(x).
- Axiom 3: Sanitize(Canon(x)) = Canon(x).
- Axiom 4: Inv(Sanitize(x)).
- Axiom 5: WF(Sanitize(x)).
2.3 Prior Guarantees
- G3: Safe(Canon(x)) for all x.
- G5 (used implicitly later): Canon is idempotent.

3. Lemmas
Lemma 1 — Collapse always returns Canon(x) on canonical input.
Proof.
From G3, Safe(Canon(x)) holds for all x.
Thus:
\mathrm{Collapse}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
□

Lemma 2 — Canon is a total function from R to Canon(R).
Proof.
Canon is defined as a composition of total operators:
- Norm: total (A2)
- ε: total
- Sanitize: total (A3)
Thus Canon(x) is defined for all x.
□

Lemma 3 — Collapse is deterministic.
Proof.
Collapse(x) is defined by a deterministic case distinction:
- If Safe(x), return Canon(x).
- Otherwise return x.
Since Safe(x) is a decidable predicate and Canon is deterministic (Lemma 2), Collapse is deterministic.
□

4. Full Proof of G4
We must show:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\; \; \Longleftrightarrow \; \; \mathrm{Canon}(x)=\mathrm{Canon}(y).
We prove both directions.

(⇒) Forward Direction
Assume:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).
We consider cases based on the definition of Collapse.

Case 1 — Safe(x) and Safe(y)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x),\quad \mathrm{Collapse}(y)=\mathrm{Canon}(y).
Thus:
\mathrm{Canon}(x)=\mathrm{Canon}(y).

Case 2 — Safe(x) and ¬Safe(y)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x),\quad \mathrm{Collapse}(y)=y.
But Collapse(x) = Collapse(y) implies:
\mathrm{Canon}(x)=y.
However, y is unsafe, while Canon(x) is always safe (G3).
Contradiction.
Thus this case is impossible.

Case 3 — ¬Safe(x) and Safe(y)
Symmetric to Case 2. Also impossible.

Case 4 — ¬Safe(x) and ¬Safe(y)
Then:
\mathrm{Collapse}(x)=x,\quad \mathrm{Collapse}(y)=y.
Collapse(x) = Collapse(y) implies:
x=y.
But for unsafe x, Canon(x) = Canon(y) follows because:
- Unsafe x and y must be identical to produce identical Collapse outputs.
- Canon is a function (Lemma 2).
Thus:
\mathrm{Canon}(x)=\mathrm{Canon}(y).

Conclusion of Forward Direction
In all possible cases:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\Rightarrow \mathrm{Canon}(x)=\mathrm{Canon}(y).
□

(⇐) Reverse Direction
Assume:
\mathrm{Canon}(x)=\mathrm{Canon}(y).
We must show:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).

Case 1 — Safe(x)
Then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
Since Canon(x) = Canon(y), we have:
\mathrm{Collapse}(x)=\mathrm{Canon}(y).
If Safe(y), then Collapse(y) = Canon(y).
If ¬Safe(y), then Collapse(y) = y, but y cannot equal Canon(y) unless y is canonical, which implies Safe(y).
Thus Safe(y) must hold.
Therefore:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y).

Case 2 — ¬Safe(x)
Then Collapse(x) = x.
But Canon(x) = Canon(y) implies that both x and y share the same canonical form.
If y were safe, Collapse(y) = Canon(y), which cannot equal x unless x = Canon(y), contradicting ¬Safe(x).
Thus y is also unsafe.
So:
\mathrm{Collapse}(x)=x=y=\mathrm{Collapse}(y).

Conclusion of Reverse Direction
\mathrm{Canon}(x)=\mathrm{Canon}(y)\Rightarrow \mathrm{Collapse}(x)=\mathrm{Collapse}(y).
□

5. Final Conclusion
Combining both directions:
\mathrm{Collapse}(x)=\mathrm{Collapse}(y)\; \; \Longleftrightarrow \; \; \mathrm{Canon}(x)=\mathrm{Canon}(y).
Thus Collapse is deterministic, reproducible, and induces the same equivalence relation as canonicalization.
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G4: Deterministic Collapse
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


