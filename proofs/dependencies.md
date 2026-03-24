
Dependency Diagram

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

This diagram makes the structure explicit:
- Axioms + Structural Assumptions → G1–G10
- G3 (Pipeline Safety) is the central dependency
- G4, G6, G7, G8, G9, G10 all rely on G3
- G5 feeds into G6 and G10
- G8 → G9 in the distributed setting
