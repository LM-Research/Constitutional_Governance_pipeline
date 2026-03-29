G8 — Distributed Safety
1. Statement
Guarantee G8 (Distributed Safety).
For a multi‑agent system with agent set A, define:
\mathrm{Safe_{dist}}(x):=\bigwedge _{a\in A}\mathrm{Safe_a}(x).
Then:
\mathrm{Safe_{dist}}(x)\quad \Longleftrightarrow \quad \forall a\in A:\  \mathrm{Safe_a}(x).
Equivalently:
- A single dissenting agent is sufficient to block distributed commitment.
- Distributed safety is the unanimous conjunction of local safety predicates.

2. Dependencies
2.1 Definitions
- Each agent a\in A has its own canonical pipeline and safety predicate:

- Distributed safety:
\mathrm{Safe_{dist}}(x):=\bigwedge _{a\in A}\mathrm{Safe_a}(x).
- Distributed quarantine:
If any agent deems x unsafe, the joint state is quarantined and cannot collapse.
2.2 Axioms and Assumptions
- Each agent implements the same canonical pipeline (Axioms 1–5).
- Each agent’s safety predicate is decidable.
- Communication is synchronous (bounded delay).
- Channels are reliable (no partitions).
- Agents are honest‑but‑curious (no Byzantine faults).
2.3 Prior Guarantees
- G3: \mathrm{Safe}(\mathrm{Canon}(x)) for each agent.
- G4: Collapse is deterministic for each agent.
- G5: Canon is idempotent for each agent.

3. Lemmas
Lemma 1 — Each agent’s safety predicate is sound.
From G3:
\mathrm{Safe_a}(\mathrm{Canon_a}(x)).
Thus each agent’s safety predicate is:
- well‑defined
- decidable
- satisfied by canonical forms
□

Lemma 2 — Distributed safety is a conjunction of local safety predicates.
This follows directly from the definition:
\mathrm{Safe_{dist}}(x):=\bigwedge _{a\in A}\mathrm{Safe_a}(x).
□

Lemma 3 — A single unsafe agent blocks distributed commitment.
If there exists a\in A such that:
\neg \mathrm{Safe_a}(x),
then:
- Agent a cannot collapse x.
- Distributed collapse requires unanimous agreement (G9).
- Thus the joint system cannot commit.
□

4. Full Proof of G8
We must show:
\mathrm{Safe_{dist}}(x)\quad \Longleftrightarrow \quad \forall a\in A:\  \mathrm{Safe_a}(x).

(⇒) Forward Direction
Assume:
\mathrm{Safe_{dist}}(x).
By definition (Lemma 2):
\bigwedge _{a\in A}\mathrm{Safe_a}(x).
Thus:
\forall a\in A:\  \mathrm{Safe_a}(x).
□

(⇐) Reverse Direction
Assume:
\forall a\in A:\  \mathrm{Safe_a}(x).
Then the conjunction over all agents holds:
\bigwedge _{a\in A}\mathrm{Safe_a}(x).
Thus:
\mathrm{Safe_{dist}}(x).
□

5. Interpretation
Distributed safety is conservative:
- If any agent detects an invariant violation, drift, or schema error,
the entire system enters quarantine.
This ensures:
- No unsafe joint commitment is possible.
- Safety is preserved under distributed composition.
- Multi‑agent systems cannot “average out” unsafe behavior.
This is the distributed analogue of G3.

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G8 — Distributed Safety
- Repo: ../assumptions/axioms.md, ../assumptions/structural_assumptions.md


