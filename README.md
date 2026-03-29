Constitutional Governance Pipeline
Minimal reference implementation of the governed representational chain described in the paper:
Constitutional Governance by Design: A Formal Architecture for Safe, Auditable AI
Lucas Mansell, 2026

This repository provides a small, deterministic, fully inspectable demonstration of the architecture:
SL → REL → SOL → Norm → ε → Sanitize → Canon → Collapse → Trace


The goal is not production readiness.
It is a runnable, auditable baseline that instantiates the paper’s formal claims in executable form, so that the axioms and guarantees can be inspected, tested, and extended.

Architecture Overview
SL — Specification Language
Files: sl_spec.yaml, credit_sl_spec.yaml
Declarative YAML schemas governing REL extraction. Each field specifies:
- name
- type
- required status
- constitutional flags (protected_proxy, latent_drift)
The invariant predicates in credit_invariants.py read these flags directly, so the invariant set adapts automatically when the schema evolves.
Two domains are included:
- Task domain (sl_spec.yaml) — minimal task/priority schema from the original implementation.
- Credit‑scoring domain (credit_sl_spec.yaml) — full four‑field schema implementing Table 1 of the paper.

REL — Representation Extraction Layer
File: rel_compiler.py
A four‑stage deterministic compiler implementing:
REL : Y → R_Σ ∪ {⊥}


Each stage is a pure, independently inspectable function:
- Lex — tokenize raw model output; detect adversarial formatting.
- Parse — construct a candidate dict; handle duplicates, omissions, and key normalization.
- TypeCheck — enforce schema types; coerce where unambiguous; raise structured failures otherwise.
- Lower — project into the SOL vocabulary and attach provenance metadata.
REL failures are first‑class constitutional events, not swallowed exceptions.
Failure types include:
|  |  | 
| omission |  | 
| misclassification |  | 
| ambiguity_collapse |  | 
| schema_drift |  | 
| adversarial_formatting |  | 



SOL — Structured Orchestrated Language
File: sol.py
Typed, finite, invariant‑addressable objects defining the constitutional space R.
- SOLObject — base class defining as_dict(), canonical(), is_well_formed(), check_invariants().
Implements the equivalence relation x≈y\Longleftrightarrow \mathrm{Canon}(x)=\mathrm{Canon}(y).
- TaskSOL — minimal task domain.
- CreditSOL — full credit‑scoring domain; enforces Table 1 invariants at the object level.

Invariants
File: credit_invariants.py
Executable predicates for Table 1:
|  |  |  |  | 
|  | ¬∃f : Proxy(f) |  |  | 
|  | ¬∃f : LatentDrift(f) |  |  | 
|  | Monotonic(income → score) |  |  | 
|  | WF(x) |  |  | 


Per‑attribute invariants prune fields during Sanitize Phase 1.
Global invariants are evaluated after pruning stabilizes; violations return ⊥.
Decidability note (Inv3).
The per‑object check enforces necessary (not sufficient) conditions for monotonicity.
Full functional monotonicity requires multi‑object reasoning and is out of scope.

Pipeline
File: pipeline.py
The canonical pipeline:
Canon(x) := Sanitize(ε(Norm(x)))


Operators:
|  |  |  | 
| norm |  | B_R | 
| epsilon |  |  | 
| sanitize |  |  | 
| canon |  | Sanitize(ε(Norm(x))) | 
| is_safe |  | Canon(x) = x | 
| collapse |  |  | 


Norm uses fixed‑point iteration rather than linear projection.
This avoids unjustified orthogonality claims and keeps the implementation honest.
Sanitize:
- Phase 1: iterative per‑attribute pruning (converges in ≤ x steps).
- Phase 2: global invariant check (global violations return ⊥).

Trace
File: trace.py
Append‑only constitutional trace implementing the (t, op, c, m) schema.
The trace is structurally inseparable from commitment:
- Collapse cannot commit without writing a trace entry.
- There is no deletion or modification of entries.
- Disabling the trace disables commitment (Guarantee 6).
All events — commits, invariant violations, REL failures, ⊥ events — are recorded.
audit_report() returns a regulator‑ready summary.

Running the Examples
pip install pyyaml
python run_example.py


Scenarios:
- Task domain round‑trip (clean).
- Credit domain clean object — commits successfully.
- Credit domain with zip_code and latent_cluster — pruned; canonical form commits.
- Credit domain with negative income — Sanitize returns ⊥; failure recorded; no commit.

Running the Tests
pip install pytest hypothesis pyyaml
pytest test_axioms.py -v


For exhaustive verification:
pytest test_axioms.py -v --hypothesis-seed=0


Test suite coverage:
|  |  | 
| TestAxiom1NormFixedPoint |  | 
| TestAxiom2RefinementFixedPoint |  | 
| TestAxiom3SanitizeFixedPoint |  | 
| TestAxiom4SanitizeRestoresInvariants |  | 
| TestAxiom5SanitizeEnforcesWellFormedness |  | 
| TestGuarantee3PipelineSafety |  | 
| TestGuarantee4DeterministicCollapse |  | 
| TestGuarantee5CanonicalIdempotence |  | 
| TestGuarantee6IrreversibilityOfCollapse |  | 
| TestGuarantee7CanonicalTraceInvariant |  | 
| TestCreditSOLInvariants |  | 
| TestBottomPropagation |  | 



File Structure
credit_sl_spec.yaml     SL specification — credit-scoring domain
credit_invariants.py    Executable invariant predicates (Table 1)
sl_spec.yaml            SL specification — task domain
sol.py                  SOLObject base class; TaskSOL; CreditSOL
rel_compiler.py         Four-stage REL compiler
pipeline.py             Norm, ε, Sanitize, Canon, Collapse
trace.py                Append-only constitutional trace
test_axioms.py          Property-based axiom and guarantee verification
run_example.py          End-to-end demonstration



Scope and Limitations
This implementation is intentionally minimal.
- Norm does not perform linear projection; it prunes to the canonical basis.
- Inv3 checks necessary conditions for monotonicity, not full functional monotonicity.
- Distributed guarantees (G8–G9) are not implemented; they require a multi‑agent context.
- Thread safety is not guaranteed; production systems should wrap trace writes in a lock.
- REL supports structured text and flat JSON; arbitrary formats require domain‑specific lexers.

License
MIT. See LICENSE.

Citation
If you use this implementation, please cite:
- L. Mansell, “Constitutional Governance by Design: A Formal Architecture for Safe, Auditable AI,” IEEE Computer, 2026 (in submission).



