
Glossary of Constitutional Governance Terms
This glossary defines all operators, predicates, and concepts used in the canonical pipeline and proof corpus.

Operators
Norm(x)
Normalization operator; eliminates representational drift.
ε(x)
Structural refinement operator; enforces structural consistency.
Sanitize(x)
Invariant‑restoring and schema‑enforcing pruning operator.
Canon(x)
Canonicalization operator:
\mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
A projection onto the constitutional subspace.
Collapse(x)
Commitment operator:
- If Safe(x), returns Canon(x)
- Otherwise returns x
Writes to the trace only when Safe(x).

Predicates
Inv(x)
Representation satisfies all invariants.
WF(x)
Representation is well‑formed under schema \Sigma .
NoDrift(x)
Representation is a fixed point of Norm.
Safe(x)
Composite predicate:
\mathrm{Safe}(x):=\mathrm{Inv}(x)\wedge \mathrm{NoDrift}(x)\wedge \mathrm{WF}(x).
Safe{}_a(x)
Agent‑local safety predicate in distributed settings.
Safe{}_{dist}(x)
Distributed safety: unanimous agreement across agents.

Spaces and Sets
R
Representational space of SOL objects.
C
Constitutional space:
C:=\{ x\in R:\mathrm{Inv}(x)\wedge \mathrm{WF}(x)\} .
Trace
Append‑only log of committed canonical states.

Distributed Concepts
Canon{}_a(x)
Canonical form computed by agent a.
Collapse{}_{dist}(x)
Distributed collapse; defined only when all agents agree on Canon(x).

Axioms 1–5
The fixed‑point and safety‑restoration laws governing Norm, ε, and Sanitize.

Guarantees G1–G10
The ten constitutional guarantees proven in /proofs.
