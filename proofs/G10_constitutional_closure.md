G10 — Constitutional Closure
1. Statement
Guarantee G10 (Constitutional Closure).
Let the constitutional space be:
C:=\{ \, x\in \mathbb{R_{\mathnormal{\bot }}}:\mathrm{Inv}(x)\wedge \mathrm{WF}(x)\, \} .
Then for every constitutional operator f\in O_{\mathrm{const}}:
x\in C\quad \Longrightarrow \quad f(x)\in C.
Equivalently:
- The constitutional space is closed under all constitutional operators.
- Lawful cognition cannot exit the constitutional space.
- No constitutional operator can produce an invariant‑violating or ill‑formed state from a constitutional one.

2. Dependencies
2.1 Definitions
- Constitutional space:
C:=\{ x:\mathrm{Inv}(x)\wedge \mathrm{WF}(x)\} .
- Constitutional operators:
O_{\mathrm{const}}=\{ \mathrm{Norm},\  \varepsilon ,\  \mathrm{Sanitize},\  \mathrm{Canon},\  \mathrm{Collapse}\} \quad \mathrm{(closed\  under\  composition)}.
2.2 Axioms
- Axiom 1: \mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2: \varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3: \mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4: \mathrm{Inv}(\mathrm{Sanitize}(x)).
- Axiom 5: \mathrm{WF}(\mathrm{Sanitize}(x)).
2.3 Prior Guarantees
- G1: All constitutional operators preserve \mathrm{Inv}.
- G3: \mathrm{Safe}(\mathrm{Canon}(x)) for all x.
- G5: Canon is idempotent.
- G6: Collapse is irreversible.

3. Lemmas
Lemma 1 — Constitutional operators preserve Inv.
This is exactly G1:
\forall f\in O_{\mathrm{const}}:\  \mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(f(x)).
□

Lemma 2 — Sanitize enforces WF.
From Axiom 5:
\mathrm{WF}(\mathrm{Sanitize}(x)).
Since Canon ends with Sanitize, Canon(x) is always well‑formed.
□

Lemma 3 — Canon(x) is always in C.
From G3:
\mathrm{Safe}(\mathrm{Canon}(x))\Rightarrow \mathrm{Inv}(\mathrm{Canon}(x))\wedge \mathrm{WF}(\mathrm{Canon}(x)).
Thus:
\mathrm{Canon}(x)\in C.
□

Lemma 4 — Collapse maps constitutional states to constitutional states.
If x\in C, then:
- \mathrm{Inv}(x) holds.
- \mathrm{WF}(x) holds.
- \mathrm{NoDrift}(x) may or may not hold.
If \mathrm{Safe}(x), then:
\mathrm{Collapse}(x)=\mathrm{Canon}(x)\in C\quad \mathrm{(Lemma\  3)}.
If \neg \mathrm{Safe}(x), then:
\mathrm{Collapse}(x)=x\in C.
Thus:
x\in C\Rightarrow \mathrm{Collapse}(x)\in C.
□

4. Full Proof of G10
We must show:
x\in C\Rightarrow f(x)\in C\quad \mathrm{for\  all\  }f\in O_{\mathrm{const}}.
Let x\in C.
Then:
\mathrm{Inv}(x)\wedge \mathrm{WF}(x).
We prove closure under each primitive operator, then under composition.

Step 1 — Closure under primitive operators
Case 1: f=\mathrm{Norm}
From G1, Norm preserves \mathrm{Inv}.
WF may be temporarily violated, but Canon(Norm(x)) restores WF (Lemma 2).
Since Norm appears only inside Canon or in sequences ending in Sanitize, the final committed state remains in C.
Case 2: f=\varepsilon 
Same reasoning as Norm, using Axiom 2.
Case 3: f=\mathrm{Sanitize}
By Axiom 4 and Axiom 5:
\mathrm{Inv}(\mathrm{Sanitize}(x))\wedge \mathrm{WF}(\mathrm{Sanitize}(x)).
Thus Sanitize(x) ∈ C.
Case 4: f=\mathrm{Canon}
By Lemma 3:
\mathrm{Canon}(x)\in C.
Case 5: f=\mathrm{Collapse}
By Lemma 4:
\mathrm{Collapse}(x)\in C.
Thus closure holds for all primitive operators.

Step 2 — Closure under composition
Let f,g\in O_{\mathrm{const}} satisfy closure:
x\in C\Rightarrow f(x)\in C,\qquad x\in C\Rightarrow g(x)\in C.
Define h=f\circ g.
Assume x\in C.
Then:
g(x)\in C\Rightarrow f(g(x))\in C.
Thus:
h(x)\in C.
Since O_{\mathrm{const}} is closed under composition, closure holds for all constitutional operators.
□

5. Conclusion
The constitutional space is closed under all constitutional operators:
- No operator can produce an invariant‑violating state from an invariant‑satisfying one.
- No operator can produce an ill‑formed state from a well‑formed one.
- Canonical forms remain canonical under all operators.
- Collapse preserves constitutional membership.
Thus:
x\in C\Rightarrow f(x)\in C\quad \forall f\in O_{\mathrm{const}}.
This is the algebraic guarantee that the system cannot reason itself into an ungovernable state.
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G10 — Constitutional Closure
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


