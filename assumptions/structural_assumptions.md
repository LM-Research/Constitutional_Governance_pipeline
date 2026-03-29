
Structural Assumptions of the Representational Space
These assumptions define the mathematical substrate required for the canonical pipeline and its constitutional guarantees. They are intentionally minimal, domain‑agnostic, and sufficient to ensure that the operators Norm, \varepsilon , Sanitize, Canon, and Collapse behave predictably and converge.

Assumption A1 — Finite Representational Space
The representational space \mathbb{R} is finite or finitely branching.
Meaning.
All operators terminate; fixed‑point iteration is well‑defined and cannot diverge.

Assumption A2 — Convergent Normalization
Repeated application of the normalization operator converges to a fixed point:
\exists n\in \mathbb{N}:\mathrm{Norm^{\mathnormal{n}}}(x)=\mathrm{Norm^{\mathnormal{n+1}}}(x).
Meaning.
Normalization eliminates representational drift and stabilizes in finite time.

Assumption A3 — Totality of Operators
All constitutional operators are total functions:
\mathrm{Norm},\  \varepsilon ,\  \mathrm{Sanitize},\  \mathrm{Canon},\  \mathrm{Collapse}:\mathbb{R_{\mathnormal{\bot }}}\rightarrow \mathbb{R_{\mathnormal{\bot }}},
where \mathbb{R_{\mathnormal{\bot }}}:=\mathbb{R}\cup \{ \bot \} .
Meaning.
Every operator produces a valid representation for every input; the pipeline never fails silently.

Assumption A4 — Decidability of Safety Predicates
The predicates
\mathrm{Inv}(x),\quad \mathrm{WF}(x),\quad \mathrm{NoDrift}(x)
are decidable.
Meaning.
Safety checks are computable and can be applied at every stage of the pipeline.

Assumption A5 — Invariant Decomposition
The invariant predicate decomposes into finitely many decidable components:
\mathrm{Inv}(x):=\bigwedge _{i=1}^k\mathrm{Inv_{\mathnormal{i}}}(x).
Meaning.
Invariant checking is modular, compositional, and amenable to mechanization.

Distributed Setting Assumptions
For multi‑agent guarantees (G8–G10), the following conditions hold:
- Synchronous communication: bounded message delay.
- Reliable channels: no partitions or message loss.
- Honest‑but‑curious agents: no Byzantine faults.
- Shared schema: all agents operate over the same schema \Sigma  and the same canonical pipeline specification.
Meaning.
These assumptions ensure that distributed canonicalization and collapse converge to a single, globally agreed‑upon representation.
