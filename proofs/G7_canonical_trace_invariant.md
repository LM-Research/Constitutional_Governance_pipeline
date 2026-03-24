
G7 — Canonical Trace Invariant
1. Statement
Guarantee G7 (Canonical Trace Invariant).
Every entry written to the constitutional trace is a canonical, safe representation:
(t,op,c,m)\in \mathrm{Trace}\quad \Rightarrow \quad c=\mathrm{Canon}(x)\; \wedge \; \mathrm{Safe}(c).
Equivalently:
- The trace never contains unsafe, malformed, drifting, or non‑canonical states.
- Only canonical forms produced by Collapse may enter the trace.

2. Dependencies
2.1 Definitions
- The trace is an append‑only sequence of tuples:
(t,op,c,m)
written only by the Collapse operator.
- Collapse:
\mathrm{Collapse}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon}(x),&\textstyle \mathrm{if\  Safe}(x)\\ \textstyle x,&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Safe(x) := Inv(x) ∧ NoDrift(x) ∧ WF(x).
- Canon(x) := Sanitize(ε(Norm(x))).
2.2 Axioms
- Axiom 1: Norm(Canon(x)) = Canon(x).
- Axiom 2: ε(Canon(x)) = Canon(x).
- Axiom 3: Sanitize(Canon(x)) = Canon(x).
- Axiom 4: Inv(Sanitize(x)).
- Axiom 5: WF(Sanitize(x)).
2.3 Prior Guarantees
- G3 (Pipeline Safety):
\mathrm{Safe}(\mathrm{Canon}(x)).- G4 (Deterministic Collapse):
Collapse(x) = Canon(x) when Safe(x).

3. Lemmas
Lemma 1 — Only Collapse writes to the trace.
Proof.
By architectural definition, the trace layer is part of the commitment boundary.
The only operator that performs a commitment is Collapse.
No other operator has write access to the trace.
□

Lemma 2 — Collapse writes Canon(x) when it writes anything.
Proof.
Collapse writes to the trace only when Safe(x) holds.
In that case:
\mathrm{Collapse}(x)=\mathrm{Canon}(x).
Thus any trace entry written by Collapse contains Canon(x) as its committed representation.
□

Lemma 3 — Canon(x) is always safe.
This is exactly G3:
\mathrm{Safe}(\mathrm{Canon}(x)).
□

4. Full Proof of G7
We must show:
(t,op,c,m)\in \mathrm{Trace}\Rightarrow c=\mathrm{Canon}(x)\wedge \mathrm{Safe}(c).
Let a trace entry be written.
By Lemma 1, it must have been written by Collapse.
Thus:
c=\mathrm{Collapse}(x)
for some x.

Step 1 — Collapse writes Canon(x)
By Lemma 2:
c=\mathrm{Canon}(x).
Thus the first half of the guarantee is satisfied.

Step 2 — Canon(x) is safe
By Lemma 3 (G3):
\mathrm{Safe}(\mathrm{Canon}(x)).
Thus:
\mathrm{Safe}(c).

Step 3 — Conjunction
Combining Steps 1 and 2:
c=\mathrm{Canon}(x)\; \wedge \; \mathrm{Safe}(c).
This holds for every trace entry.
□

5. Conclusion
The canonical trace invariant follows from:
- Collapse being the only operator that writes to the trace.
- Collapse writing only canonical forms.
- Canonical forms being always safe (G3).
Thus the trace is constitutionally clean:
- no unsafe states
- no malformed states
- no drifting states
- no non‑canonical states
ever appear in the audit log.
This is the architectural foundation for Article 12 traceability and for complete, structural auditability.
□

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G7: Canonical Trace Invariant
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


