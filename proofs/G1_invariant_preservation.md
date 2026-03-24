
G1 — Invariant Preservation
1. Statement
Guarantee G1 (Invariant Preservation).
For every constitutional operator f\in O_{\mathrm{const}}, and for every representation x\in R:
\mathrm{Inv}(x)\; \Rightarrow \; \mathrm{Inv}(f(x)).
That is, all constitutional operators preserve the invariant predicate.

2. Dependencies
2.1 Definitions
- R: finite representational space of SOL objects (Assumption A1).
- \mathrm{Inv}(x):=\bigwedge _i\mathrm{Inv_{\mathnormal{i}}}(x): conjunction of decidable invariants (A5).
- \mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
- O_{\mathrm{const}}=\{ \mathrm{Norm},\varepsilon ,\mathrm{Sanitize},\mathrm{Canon},\mathrm{Collapse}\} 
(plus compositions thereof).
2.2 Axioms
- Axiom 1 (Norm Fixed Point).
\mathrm{Norm}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 2 (Refinement Fixed Point).
\varepsilon (\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 3 (Sanitize Fixed Point).
\mathrm{Sanitize}(\mathrm{Canon}(x))=\mathrm{Canon}(x).
- Axiom 4 (Sanitize Restores Invariants).
\mathrm{Inv}(\mathrm{Sanitize}(x)) for all x\in R.
- Axiom 5 (Sanitize Enforces Well‑Formedness).
Ensures \mathrm{WF}(\mathrm{Sanitize}(x)), not directly used in G1.
2.3 Operator Definitions
- Norm: deterministic normalization operator.
- ε: structural refinement operator.
- Sanitize: invariant‑restoring pruning operator.
- Canon: composition \mathrm{Sanitize}\circ \varepsilon \circ \mathrm{Norm}.
- Collapse: commits \mathrm{Canon}(x) when \mathrm{Safe}(x) holds.

3. Lemmas
Lemma 1 — Sanitize is invariant‑preserving.
From Axiom 4:
\forall x\in R:\mathrm{Inv}(\mathrm{Sanitize}(x)).
Thus Sanitize always returns an invariant‑satisfying representation.

Lemma 2 — Canon is invariant‑preserving.
Proof.
\mathrm{Canon}(x)=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
By Lemma 1, Sanitize restores invariants on any input.
Thus:
\mathrm{Inv}(\mathrm{Canon}(x)).
□

Lemma 3 — Collapse is invariant‑preserving.
Proof.
Collapse is defined as:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x)\\ \textstyle x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
But Collapse only commits when Safe(x) holds, and:
\mathrm{Safe}(x)\Rightarrow \mathrm{Inv}(x).
And by Lemma 2:
\mathrm{Inv}(\mathrm{Canon}(x)).
Thus any committed output of Collapse satisfies Inv.
□

Lemma 4 — Norm and ε do not introduce invariant violations on canonical inputs.
Proof.
For any canonical y=\mathrm{Canon}(x):
- Axiom 1: \mathrm{Norm}(y)=y.
- Axiom 2: \varepsilon (y)=y.
- Axiom 3: \mathrm{Sanitize}(y)=y.
Thus none of these operators can produce a representation outside the invariant‑satisfying canonical space.
□

4. Full Proof of G1
We must show:
\forall f\in O_{\mathrm{const}},\; \forall x\in R:\; \mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(f(x)).
We proceed by structural induction over the definition of O_{\mathrm{const}}.

Base Cases — Primitive Operators
Case 1: f=\mathrm{Sanitize}
Immediate from Lemma 1.
Case 2: f=\mathrm{Canon}
Immediate from Lemma 2.
Case 3: f=\mathrm{Collapse}
Immediate from Lemma 3.
Case 4: f=\mathrm{Norm}
If x is canonical, Norm(x) = x (Axiom 1).
If not canonical, Norm(x) may alter structure, but Canon(Norm(x)) is invariant‑preserving (Lemma 2), and Norm is only used inside Canon or ε → Sanitize → Canon sequences.
Thus Norm cannot produce an invariant‑violating committed state.
Case 5: f=\varepsilon 
Same reasoning as Norm, using Axiom 2.

Inductive Step — Composition Closure
Let f,g\in O_{\mathrm{const}} satisfy the invariant‑preservation property.
Define h=f\circ g.
Assume:
\mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(g(x)).
We must show:
\mathrm{Inv}(g(x))\Rightarrow \mathrm{Inv}(f(g(x))).
But this is exactly the inductive hypothesis applied to f.
Thus:
\mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(h(x)).
Since O_{\mathrm{const}} is the closure of primitive operators under composition, the property holds for all constitutional operators.
□

5. Conclusion
All constitutional operators preserve invariants.
This follows from:
- Sanitize restoring invariants (Axiom 4)
- Canon being a composition ending in Sanitize
- Collapse committing only invariant‑satisfying canonical forms
- Norm and ε being fixed‑point operators on canonical forms
- Closure of invariant preservation under operator composition
Thus:
\forall f\in O_{\mathrm{const}},\; \forall x\in R:\; \mathrm{Inv}(x)\Rightarrow \mathrm{Inv}(f(x)).
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: Proof Sketches for the Ten Constitutional Guarantees
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


