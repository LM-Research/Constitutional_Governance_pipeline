
G9 — Distributed Agreement
1. Statement
Guarantee G9 (Distributed Agreement).
For a multi‑agent system with agent set A, distributed collapse is defined if and only if all agents compute the same canonical form:
\mathrm{Collapse_{dist}}(x)\; \mathrm{is\  defined}\quad \Longleftrightarrow \quad \forall a,b\in A:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x).
Equivalently:
- Joint commitment requires unanimous canonical agreement.
- If any agent computes a different canonical form, distributed collapse is undefined and no commitment occurs.

2. Dependencies
2.1 Definitions
- Each agent a\in A has its own canonical pipeline:
\mathrm{Canon_{\mathnormal{a}}}(x):=\mathrm{Sanitize_{\mathnormal{a}}}(\varepsilon _a(\mathrm{Norm_{\mathnormal{a}}}(x))).
- Distributed collapse:
\mathrm{Collapse_{dist}}(x)=\left\{ \, \begin{array}{ll}\textstyle \mathrm{Canon_{\mathnormal{a}}}(x),&\textstyle \mathrm{if\  }\forall a,b:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x)\\ \textstyle \mathrm{undefined},&\textstyle \mathrm{otherwise}.\end{array}\right. 
- Agents broadcast their canonical forms before joint commitment.
2.2 Axioms and Assumptions
- All agents share the same SOL schema \Sigma .
- All agents implement the same canonical pipeline specification (Axioms 1–5).
- Communication is synchronous (bounded delay).
- Channels are reliable.
- Agents are honest‑but‑curious (no Byzantine faults).
2.3 Prior Guarantees
- G3: Safe(Canon{}_a(x)) for each agent.
- G4: Collapse{}_a(x) = Canon{}_a(x) when Safe{}_a(x).
- G5: Canon{}_a(Canon{}_a(x)) = Canon{}_a(x).
- G8: Distributed safety requires unanimous local safety.

3. Lemmas
Lemma 1 — Canonical forms are deterministic within each agent.
From G4 and G5:
\mathrm{Canon_{\mathnormal{a}}}(x)\mathrm{\  is\  deterministic\  and\  idempotent}.
Thus each agent computes a unique canonical form for any input.
□

Lemma 2 — Distributed collapse requires agreement on canonical forms.
Proof.
By definition, distributed collapse is defined only when:
\forall a,b\in A:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x).
If this condition fails, the joint commitment is undefined.
□

Lemma 3 — If canonical forms agree, distributed collapse is well‑defined.
Proof.
If:
\forall a,b:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x)=c,
then the joint system commits to c.
Since c is identical across all agents, the choice of agent is irrelevant.
□

4. Full Proof of G9
We must show:
\mathrm{Collapse_{dist}}(x)\mathrm{\  is\  defined}\quad \Longleftrightarrow \quad \forall a,b:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x).

(⇒) Forward Direction
Assume:
\mathrm{Collapse_{dist}}(x)\mathrm{\  is\  defined}.
By definition of distributed collapse, this is possible only if:
\forall a,b:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x).
Thus the forward direction holds immediately.
□

(⇐) Reverse Direction
Assume:
\forall a,b:\; \mathrm{Canon_{\mathnormal{a}}}(x)=\mathrm{Canon_{\mathnormal{b}}}(x)=c.
We must show:
\mathrm{Collapse_{dist}}(x)=c.
Since all agents compute the same canonical form:
- Each agent’s local collapse (if Safe{}_a(x)) yields c.
- By G8, if any agent is unsafe, distributed safety fails and collapse is blocked.
- If all agents are safe, distributed collapse commits to c.
Thus distributed collapse is defined and equals c.
□

5. Interpretation
Distributed agreement is the structural guarantee that:
- No agent can unilaterally commit the system.
- No joint commitment can occur unless all agents compute the same canonical form.
- Canonical disagreement blocks commitment, preventing unsafe or inconsistent distributed states.
This is the distributed analogue of G4 (Deterministic Collapse), extended to multi‑agent systems.

6. Cross‑References
- Paper Section: 4. The Formal Substrate and Its Guarantees
- Appendix A: G9: Distributed Agreement
- Axioms: Section 4.3 — The Formal Substrate: Five Axioms
- Repo: /assumptions/axioms.md, /assumptions/structural_assumptions.md


