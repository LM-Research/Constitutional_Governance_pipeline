
Dependency Structure of the Constitutional Guarantees
This document describes the formal dependency graph connecting the axioms, structural assumptions, intermediate lemmas, and the ten constitutional guarantees (G1–G10). It makes explicit how the guarantees derive from the foundational mathematical substrate defined in ../assumptions/.

Mermaid Dependency Graph

graph TD

    Axioms["Axioms 1–5"] --> G1
    Axioms --> G2
    Axioms --> G3
    Axioms --> G4
    Axioms --> G5
    Axioms --> G6
    Axioms --> G7
    Axioms --> G8
    Axioms --> G9
    Axioms --> G10

    Struct["Structural Assumptions A1–A5"] --> G1
    Struct --> G2
    Struct --> G3
    Struct --> G4
    Struct --> G5
    Struct --> G6
    Struct --> G7
    Struct --> G8
    Struct --> G9
    Struct --> G10

    G1 --> G3
    G2 --> G3
    G3 --> G4
    G3 --> G6
    G3 --> G7
    G3 --> G8
    G3 --> G9
    G3 --> G10

    G4 --> G6
    G5 --> G6
    G5 --> G10

    G8 --> G9



ASCII Overview

                 +---------------------------+
                 |   Structural Assumptions  |
                 |        A1 – A5            |
                 +-------------+-------------+
                               |
                               v
+------------------------------+------------------------------+
|                              |                              |
v                              v                              v
G1 <------------------------ Axioms ------------------------> G2
|                               |                              |
v                               v                              v
G3 (Pipeline Safety) <-----------+-----------------------------+
| \            \            \           \           \          |
|  \            \            \           \           \         |
v   v            v            v           v           v        v
G4  G6           G7           G8          G9          G10      G5



Interpretation of the Dependency Graph
The diagram captures the logical structure of the constitutional architecture:
1. Axioms + Structural Assumptions → All Guarantees
Every constitutional guarantee G_i depends directly on:
- the Axioms (A1–A5), and
- the Structural Assumptions (S1–S5).
These form the mathematical substrate of the system.

2. G3 (Pipeline Safety) is the central dependency
Guarantee G3 — Pipeline Safety — is the pivotal lemma in the system.
It is required for:
- G4 (Deterministic Collapse)
- G6 (Irreversibility)
- G7 (Canonical Trace Invariant)
- G8 (Distributed Safety)
- G9 (Distributed Agreement)
- G10 (Constitutional Closure)
This reflects the fact that the canonical pipeline is the backbone of the entire architecture.

3. G5 (Canonical Idempotence) feeds into G6 and G10
Idempotence is essential for:
- proving irreversibility (G6), and
- establishing closure under repeated collapse (G10).

4. Distributed guarantees form a chain
In the distributed setting:
- G8 (Distributed Safety) → G9 (Distributed Agreement)
This reflects the standard structure of distributed fixed‑point systems:
safety precedes agreement.

Summary
The dependency graph makes explicit the formal structure of the constitutional governance architecture:
\mathrm{Assumptions}\; \Rightarrow \; \mathrm{Axioms}\; \Rightarrow \; \mathrm{Lemmas}\; \Rightarrow \; \mathrm{Guarantees}.
This file provides the global map that ties the entire proof corpus together.
