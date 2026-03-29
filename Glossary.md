Glossary of Constitutional Governance Terms
This glossary defines all operators, predicates, spaces, and distributed concepts used in the canonical pipeline and the formal proof corpus.

Operators
Norm(x)
Normalization operator. Eliminates representational drift and converges to a fixed point under finite iteration (Axiom 1, A2).
ε(x)
Structural refinement operator. Enforces structural consistency and resolves representational ambiguities (Axiom 2).
Sanitize(x)
Invariant‑restoring and schema‑enforcing pruning operator.
- Removes unsafe fields (per‑attribute invariants).
- Enforces well‑formedness (Axiom 5).
- Restores invariants (Axiom 4).
- Final stage of the canonical pipeline.
Canon(x)
Canonicalization operator:
\mathrm{Canon}(x):=\mathrm{Sanitize}(\varepsilon (\mathrm{Norm}(x))).
A projection onto the constitutional subspace.
Idempotent (G5), drift‑free (G2), invariant‑satisfying and well‑formed (G3).
Collapse(x)
Commitment operator:
- If Safe(x), returns Canon(x) and writes to the trace.
- Otherwise returns x unchanged.
Deterministic (G4) and irreversible (G6).

Predicates
Inv(x)
Representation satisfies all invariants (per‑attribute and global).
WF(x)
Representation is well‑formed under schema \Sigma .
Enforced by Sanitize (Axiom 5).
NoDrift(x)
Representation is a fixed point of Norm:
\mathrm{Norm}(x)=x.
Safe(x)
Composite safety predicate:
\mathrm{Safe}(x):=\mathrm{Inv}(x)\wedge \mathrm{NoDrift}(x)\wedge \mathrm{WF}(x).
Canonical forms always satisfy Safe (G3).
Safe_a(x)
Agent‑local safety predicate in distributed settings.
Safe_{dist}(x)
Distributed safety predicate:
\mathrm{Safe_{dist}}(x):=\bigwedge _{a\in A}\mathrm{Safe_a}(x).
Requires unanimous agreement (G8).

Spaces and Sets
R
Representational space of SOL objects. Finite or finitely branching (A1).
C
Constitutional space:
C:=\{ x\in R:\mathrm{Inv}(x)\wedge \mathrm{WF}(x)\} .
Closed under all constitutional operators (G10).
Trace
Append‑only log of committed canonical states.
Only Collapse writes to the trace (G7).

Distributed Concepts
Canon_a(x)
Canonical form computed by agent a. Deterministic and idempotent (G4, G5).
Collapse_{dist}(x)
Distributed collapse. Defined only when all agents compute the same canonical form:
\forall a,b:\  \mathrm{Canon_a}(x)=\mathrm{Canon_b}(x).
Unanimous agreement required (G9).

Axioms 1–5
The fixed‑point and safety‑restoration laws governing Norm, ε, and Sanitize:
- Norm Fixed Point
- Refinement Fixed Point
- Sanitize Fixed Point
- Sanitize Restores Invariants
- Sanitize Enforces Well‑Formedness
These axioms define the canonical pipeline.

Guarantees G1–G10
The ten constitutional guarantees proven in /proofs:
- G1: Invariant Preservation
- G2: Drift Elimination
- G3: Pipeline Safety
- G4: Deterministic Collapse
- G5: Canonical Idempotence
- G6: Irreversibility of Collapse
- G7: Canonical Trace Invariant
- G8: Distributed Safety
- G9: Distributed Agreement
- G10: Constitutional Closure
These guarantees collectively define the safety, determinism, and auditability of the architecture.
