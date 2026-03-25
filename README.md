
# Constitutional Governance Pipeline

Minimal reference implementation of the governed representational chain
described in the paper:

> **Constitutional Governance by Design: A Formal Architecture for Safe,
> Auditable AI**
> Lucas Mansell, 2026

The repository provides a small, deterministic, fully inspectable
demonstration of the architecture:

    SL → REL → SOL → Norm → ε → Sanitize → Canon → Collapse → Trace

The goal is not a production system. It is a runnable, auditable baseline
that instantiates the paper's formal claims in executable form, so that
the axioms and guarantees can be inspected, tested, and extended.

---

## Architecture

### SL — Specification Language (`sl_spec.yaml`, `credit_sl_spec.yaml`)

Declarative YAML schemas governing REL extraction. Each field entry
specifies its name, type, required status, and constitutional flags
(`protected_proxy`, `latent_drift`). The invariant predicates in
`credit_invariants.py` read these flags directly, so the invariant set
adapts when the schema changes without requiring edits to predicate code.

Two domains are provided:
- **Task domain** (`sl_spec.yaml`): minimal task/priority schema retained
  from the original implementation.
- **Credit-scoring domain** (`credit_sl_spec.yaml`): full four-field schema
  implementing Table 1 of the paper, including proxy and drift-flagged
  fields.

### REL — Representation Extraction Layer (`rel_compiler.py`)

A four-stage deterministic compiler implementing:

    REL : Y → R_Σ ∪ {⊥}

The four stages are independently inspectable pure functions:

1. **Lex** — segment raw model output (text or JSON) into
   `(key, raw_value)` tokens. Detects adversarial formatting heuristically.
2. **Parse** — construct a candidate attribute-value dict. Handles
   duplicate keys (last-value-wins, logged), missing required fields
   (`omission` failure), and key normalisation.
3. **TypeCheck** — enforce schema-level type constraints. Coerces where
   unambiguous; falls back to schema defaults; raises `RELFailure` on
   unresolvable misclassification.
4. **Lower** — project into the SOL canonical attribute vocabulary and
   attach provenance metadata (REL version, SL spec version, model
   version, extraction timestamp).

REL failures are first-class constitutional events, not exceptions to be
swallowed. All failures are of a bounded, named type:

| Type | Description |
|---|---|
| `omission` | Required field absent from model output |
| `misclassification` | Value not coercible to declared type |
| `ambiguity_collapse` | Duplicate key; last value used (non-fatal) |
| `schema_drift` | Field present in output but not in schema |
| `adversarial_formatting` | Output structure defeats extraction |

### SOL — Structured Orchestrated Language (`sol.py`)

Typed, finite, invariant-addressable objects defining the constitutional
space R. All committed states are SOL objects.

- **`SOLObject`** — abstract base class defining the interface:
  `as_dict()`, `canonical()`, `is_well_formed()`, `check_invariants()`.
  Implements the paper's equivalence relation `x ≈ y ⟺ Canon(x) = Canon(y)`
  via `__eq__`.
- **`TaskSOL`** — minimal task/priority domain.
- **`CreditSOL`** — full credit-scoring domain. Implements Table 1 in full
  as an object-level second enforcement point independent of the pipeline.

### Invariants (`credit_invariants.py`)

Executable predicates for Table 1 of the paper:

| Id | Predicate | Type | Encodes |
|---|---|---|---|
| Inv1 | `¬∃f : Proxy(f)` | per-attribute | Fairness |
| Inv2 | `¬∃f : LatentDrift(f)` | per-attribute | Robustness |
| Inv3 | `Monotonic(income → score)` | global | Validity |
| Inv4 | `WF(x)` | global | Structural |

**Per-attribute invariants** (Inv1, Inv2) are evaluated field-by-field
during Sanitize Phase 1. Fields that violate them are pruned.

**Global invariants** (Inv3, Inv4) are evaluated over the residual object
after Phase 1 stabilises. A global violation cannot be resolved by
pruning a single field; Sanitize returns ⊥ and the failure is recorded
in the trace.

**Decidability note on Inv3.** `Monotonic(income → score)` is formally
a property of the scoring function across objects. Its per-object
decidable instantiation — verified here — checks that `income > 0` and
`credit_score ∈ [0, 1]`, which are necessary but not sufficient conditions
for a monotone scorer. Full monotonicity requires a multi-object witness
set or a functional specification of the scorer, both outside the scope
of this reference implementation. Domain engineers extending this example
should not interpret the per-object check as a sufficient monotonicity
guarantee.

### Pipeline (`pipeline.py`)

The canonical pipeline `Canon(x) := Sanitize(ε(Norm(x)))` implemented
as distinct, independently inspectable operators:

| Operator | Axiom satisfied | Description |
|---|---|---|
| `norm` | Axiom 1 | Aligns to canonical basis B_R via fixed-point iteration |
| `epsilon` | Axiom 2 | Enforces syntactic/semantic well-formedness |
| `sanitize` | Axioms 3–5 | Two-phase invariant pruning; returns ⊥ if none exists |
| `canon` | Guarantees 3–5 | Composition: `Sanitize(ε(Norm(x)))` |
| `is_safe` | Guarantee 3 | True iff `Canon(x) = x` |
| `collapse` | Guarantees 4, 6 | Commits safe representations to the trace |

**Norm** uses documented fixed-point iteration rather than a linear
projection onto a protected-attribute-free subspace. A projection would
be semantically richer but would make orthogonality claims that this
reference implementation cannot support empirically. The fixed-point
approach is honest about scope.

**Sanitize** runs in two phases:
- Phase 1: iterative per-attribute pruning until fixed point
  (convergence guaranteed in at most `|x|` steps by Axiom A1).
- Phase 2: global invariant check over the residual object.
  Global violations return ⊥ rather than a pruned object, because
  no single field removal can resolve a relational constraint failure.

### Trace (`trace.py`)

Append-only constitutional trace implementing the `(t, op, c, m)` schema.

The trace is not a monitoring overlay. It is structurally inseparable
from commitment: `Collapse` cannot write a canonical form without writing
a trace entry, and there is no mechanism to delete or modify entries after
the fact. Disabling the trace disables `Collapse`.

All events — successful commits, invariant violations, REL failures, and
⊥ events — are recorded as first-class constitutional trace events.
`audit_report()` returns a summary dict suitable for JSON export to a
regulator-facing audit surface.

---

## Running the examples
```bash
pip install pyyaml
python run_example.py
```

Expected output covers four scenarios:
1. Task domain round-trip (clean).
2. Credit domain clean object — commits successfully.
3. Credit domain with `zip_code` and `latent_cluster` present —
   Sanitize prunes both fields; canonical form commits successfully.
4. Credit domain with negative income — Sanitize returns ⊥; failure
   recorded in trace; no commitment occurs.

---

## Running the tests
```bash
pip install pytest hypothesis pyyaml
pytest test_axioms.py -v
```

For exhaustive pre-submission verification:
```bash
pytest test_axioms.py -v --hypothesis-seed=0
```

The test suite verifies:

| Test class | Formal property |
|---|---|
| `TestAxiom1NormFixedPoint` | Axiom 1: `Norm(Canon(x)) = Canon(x)` |
| `TestAxiom2RefinementFixedPoint` | Axiom 2: `ε(Canon(x)) = Canon(x)` |
| `TestAxiom3SanitizeFixedPoint` | Axiom 3: `Sanitize(Canon(x)) = Canon(x)` |
| `TestAxiom4SanitizeRestoresInvariants` | Axiom 4: `Inv(Sanitize(x))` |
| `TestAxiom5SanitizeEnforcesWellFormedness` | Axiom 5: `WF(Sanitize(x))` |
| `TestGuarantee3PipelineSafety` | Guarantee 3: `Safe(Canon(x))` |
| `TestGuarantee4DeterministicCollapse` | Guarantee 4: deterministic collapse |
| `TestGuarantee5CanonicalIdempotence` | Guarantee 5: `Canon(Canon(x)) = Canon(x)` |
| `TestGuarantee6IrreversibilityOfCollapse` | Guarantee 6: append-only trace |
| `TestGuarantee7CanonicalTraceInvariant` | Guarantee 7: all commits are safe |
| `TestCreditSOLInvariants` | Table 1 invariants at the object level |
| `TestBottomPropagation` | ⊥ propagates cleanly through all operators |

---

## File structure
```
credit_sl_spec.yaml     SL specification — credit-scoring domain
credit_invariants.py    Executable invariant predicates (Table 1)
sl_spec.yaml            SL specification — task domain (original)
sol.py                  SOLObject base class; TaskSOL; CreditSOL
rel_compiler.py         Four-stage REL compiler
pipeline.py             Norm, ε, Sanitize, Canon, Collapse
trace.py                Append-only constitutional trace
test_axioms.py          Property-based axiom and guarantee verification
run_example.py          End-to-end demonstration (four scenarios)
```

---

## Scope and limitations

This implementation is intentionally minimal. It is a specification
baseline, not a production system.

- **Norm** does not perform linear projection. It removes fields outside
  the canonical basis via fixed-point iteration. Domain engineers requiring
  true feature orthogonalization should treat this as a documented extension
  point.
- **Inv3** verifies necessary conditions for monotonicity per object, not
  functional monotonicity across objects. See the decidability note above.
- **Distributed guarantees** (Guarantees 8 and 9) are not implemented.
  They require a multi-agent deployment context outside the scope of this
  reference implementation.
- **Thread safety** is not guaranteed. Production deployments should
  wrap `trace._append` in a lock or replace it with an external
  append-only log backend.
- The **REL compiler** supports structured text and flat JSON inputs.
  Arbitrary model output formats require domain-specific lexer extensions.

---

## License

MIT. See `LICENSE`.

---

## Citation

If you use this implementation in your own work, please cite the paper:

> L. Mansell, "Constitutional Governance by Design: A Formal Architecture
> for Safe, Auditable AI," *IEEE Computer*, 2026 (in submission).