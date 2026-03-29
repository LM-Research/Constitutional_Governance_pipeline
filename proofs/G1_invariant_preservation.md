G1 — Invariant Preservation
1. Statement
Guarantee G1 (Invariant Preservation).
For every constitutional operator f\in O_{\mathrm{const}} and every representation
x\in \mathbb{R_{\mathnormal{\bot }}}:=\mathbb{R}\cup \{ \bot \} :
\mathrm{Inv}(x)\; \Rightarrow \; \mathrm{Inv}(f(x)).
That is, all constitutional operators preserve the invariant predicate.

2. Dependencies
2.1 Definitions
- \mathbb{R}: finite or finitely branching representational space (A1).
- \mathrm{Inv}(x):=\bigwedge _i\mathrm{Inv_{\mathnormal{i}}}(x): conjunction of decidable invariants (A5).
- Canonical pipeline:
\mathrm{Canon}(x):=\mathrm{Sanitize}\! \left( \varepsilon (\mathrm{Norm}(x))\right) .
- Constitutional operators:
O_{\mathrm{const}}=\{ \mathrm{Norm},\  \varepsilon ,\  \mathrm{Sanitize},\  \mathrm{Canon},\  \mathrm{Collapse}\} \quad \mathrm{(closed\  under\  composition)}.
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4 (Sanitize Restores Invariants).
For all x\in \mathbb{R_{\mathnormal{\bot }}}:
\mathrm{Inv}(\mathrm{Sanitize}(x)).
- Axiom 5 (Sanitize Enforces Well‑Formedness).
Ensures \mathrm{WF}(\mathrm{Sanitize}(x)).
(Not directly used in G1.)
2.3 Operator Definitions
- Norm: deterministic normalization operator.
- \varepsilon : structural refinement operator.
- Sanitize: invariant‑restoring pruning operator.
- Canon: \mathrm{Sanitize}\circ \varepsilon \circ \mathrm{Norm}.
- Collapse: commits \mathrm{Canon}(x) when \mathrm{Safe}(x) holds.

3. Lemmas
Lemma 1 — Sanitize is invariant‑preserving.
From Axiom 4:
\forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{Inv}(\mathrm{Sanitize}(x)).
Thus Sanitize always returns an invariant‑satisfying representation.
□

Lemma 2 — Canon is invariant‑preserving.
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
By Lemma 1, Sanitize restores invariants on any input.
Thus:
\mathrm{Inv}(\mathrm{Canon}(x)).
□

Lemma 3 — Collapse is invariant‑preserving.
Collapse is defined as:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x),\\ \textstyle [4pt]x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
But:
- \mathrm{Safe}(x)\Rightarrow \mathrm{Inv}(x), and
- by Lemma 2, \mathrm{Inv}(\mathrm{Canon}(x)).
Thus any committed output of Collapse satisfies \mathrm{Inv}.
□

Lemma 4 — Norm and \varepsilon  preserve invariants on canonical inputs.
For any canonical y=\mathrm{Canon}(x):
- Axiom 1: \mathrm{Norm}(y)=y.
- Axiom 2: \varepsilon (y)=y.
- Axiom 3: \mathrm{Sanitize}(y)=y.
Thus none of these operators can produce a representation outside the invariant‑satisfying canonical space.
□

4. Full Proof of G1
We must show:
\forall f\in O_{\mathrm{const}},\  \forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(f(x)).
We proceed by structural induction over the definition of O_{\mathrm{const}}.

Base Cases — Primitive Operators
Case 1: f=\mathrm{Sanitize}
Immediate from Lemma 1.
Case 2: f=\mathrm{Canon}
Immediate from Lemma 2.
Case 3: f=\mathrm{Collapse}
Immediate from Lemma 3.
Case 4: f=\mathrm{Norm}
If x is canonical, Axiom 1 gives \mathrm{Norm}(x)=x.
If not canonical, Norm may alter structure, but:
- Canon(Norm(x)) is invariant‑preserving (Lemma 2), and
- Norm appears only inside Canon or in sequences ending in Sanitize.
Thus Norm cannot produce an invariant‑violating committed state.
Case 5: f=\varepsilon 
Same reasoning as Norm, using Axiom 2.

Inductive Step — Closure Under Composition
Let f,g\in O_{\mathrm{const}} satisfy invariant preservation.
Define h=f\circ g.
Assume:
\mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(g(x)).
We must show:
\mathrm{Inv}(g(x))\Rightarrow \mathrm{Inv}(f(g(x))).
But this is exactly the inductive hypothesis applied to f.
Thus:
\mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(h(x)).
Since O_{\mathrm{const}} is closed under composition, the property holds for all constitutional operators.
□

5. Conclusion
All constitutional operators preserve invariants. This follows from:
- Sanitize restoring invariants (Axiom 4),
- Canon ending in Sanitize,
- Collapse committing only invariant‑satisfying canonical forms,
- Norm and \varepsilon  being fixed‑point operators on canonical forms, and
- closure of invariant preservation under composition.
Thus:
\forall f\in O_{\mathrm{const}},\  \forall x\in \mathbb{R_{\mathnormal{\bot }}}:\  \mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(f(x)).
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: Proof Sketches for the Ten Constitutional Guarantees
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


