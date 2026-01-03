# AJT Negative Proof Simulation

This repository demonstrates how a minimal, audit-aligned Judgment Trace (AJT)
can be extended to provide **Negative Proof**:
verifiable evidence of what an AI system explicitly blocked.

This is a **standalone simulation** intended for audit and accountability discussions.

---

## ⚠️ Important Disclaimer

**This is a controlled simulation for audit rehearsal.**

- Uses a **deterministic stub** (not real LLMs) to guarantee reproducibility
- The goal is to demonstrate **negative proof via AJT logging**, not real-world safety or enforcement
- Not a production system — this is a proof-of-concept for accountability mechanisms
- **All policies, cases, and inputs are synthetic and for demonstration purposes only**

---

## ⚠️ Scope

**This project does NOT claim:**
- ❌ Correctness of AI outputs
- ❌ Legal compliance guarantees
- ❌ Safety or harm prevention

**This project DOES demonstrate:**
- ✅ **Auditability of decision boundaries** via structured logs
- ✅ Reproducible evidence trails for post-incident accountability
- ✅ Separation of LLM generation from policy enforcement

This is a **simulation for audit rehearsal**, not a production compliance tool.

---

## What this shows

- How blocked decision paths can be logged as evidence
- Clear separation between generation and judgment
- Reproducible audit replay using hashes (policy + run)

---

## What this does NOT show

- Model explainability or chain-of-thought
- Policy correctness or normative claims
- Harm prevention or safety guarantees

---

## Relation to AJT Spec

This simulation uses the minimal Judgment Trace (AJT) schema defined in:

**https://github.com/Nick-heo-eg/spec**

- The spec is used **as-is**
- No modifications or extensions to the spec are proposed
- Negative Proof is implemented as an **optional extension layer**

This repository depends only on the public AJT specification
and is intentionally decoupled from any internal systems.

---

## Architecture

```
User Input
    ↓
┌─────────────────────────────┐
│  Candidate Generator (LLM)  │  ← Deterministic stub (no real API)
│  Generates 3-5 candidates   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Judgment Layer             │  ← Explicit rules from YAML policy
│  - Applies rules in order   │
│  - Blocks violations        │
│  - Emits Negative Proof     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Final Decision + Log       │
│  - Selected response        │
│  - Decision basis (rules)   │
│  - Negative Proof records   │
│  - AJT record (spec)        │
│  - Reproducibility hash     │
└─────────────────────────────┘
```

**Key principle:**
The LLM generates. The Judgment Layer decides.

---

## Case: Air Canada Chatbot Misinformation

### Scenario
User asks about bereavement fare refunds. LLM may hallucinate that retroactive refunds are possible.

### Policy Rules
1. **R1: Source-of-truth enforcement** — Block responses contradicting official refund policy
2. **R2: Citation requirement** — Require citation to official policy
3. **R3: Confidence threshold** — Block low-confidence responses (< 0.75)

### Example Result
```json
{
  "decision": "allow",
  "selected_candidate": "aircanada_candidate_1",
  "negative_proof_count": 6,
  "blocked_by_rules": [
    "R1_source_of_truth_enforcement",
    "R2_require_citation",
    "R3_confidence_threshold"
  ]
}
```

**Coverage:** 3 out of 4 candidates blocked = 75% would have been policy violations without Judgment Layer

---

## Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run simulation
PYTHONPATH=. python -m sim.run --case aircanada --seed 42 --out logs/demo.json

# Run tests
pytest -v
```

**Expected output:**
```
✓ Simulation complete: aircanada
  Policy: 1.0.0 (960abe31...)
  Candidates: 4
  Negative Proofs: 6
  Final Decision: allow
  Run Hash: 82960705...
```

---

## Log Structure

Each run produces a JSON log with:

- **Candidates** (all generated options)
- **Decision basis** (selected candidate + applied rule IDs)
- **Negative Proof** (blocked candidates with reasons)
- **AJT record** (spec-compliant, 9 required fields + extensions)
- **Reproducibility** (seed + policy hash + run hash)

---

## Design Principles

1. **Fail closed** — If logging fails, no decision is emitted
2. **No silent failures** — Blocks and failures are explicit
3. **Log, don't enforce** — This is an audit trail, not a policy engine

---

## Testing

- **22 passing tests** including:
  - Reproducibility (same seed → identical output)
  - Negative Proof presence (blocks generate logs)
  - AJT spec compliance (9 required fields)
  - Policy hash lock (changes detected)

---

## Failure Modes

**Logging Failure Behavior:**
- If AJT logging fails → system fails closed (no decision emitted)
- If policy file missing → simulation aborts with error
- If hash mismatch detected → audit trail integrity compromised (logged)

**Design principle:** Silence is not an option. Failures are explicit.

---

## File Structure

```
ajt-negative-proof-sim/
├── README.md
├── requirements.txt
├── sim/
│   ├── run.py                         # CLI entry point
│   ├── core/
│   │   ├── candidate_generator.py     # Deterministic LLM stub
│   │   ├── judgment_layer.py          # Rule application engine
│   │   ├── ajt_record.py              # AJT spec implementation
│   │   ├── log_schema.py              # Pydantic models
│   │   └── hash_utils.py              # SHA256 hashing
│   ├── cases/
│   │   └── aircanada_case.py          # Air Canada case spec
│   ├── policies/
│   │   └── policy_aircanada.yaml      # Policy rules
│   ├── fixtures/
│   │   └── aircanada_inputs.json      # Input test data
│   └── tests/
│       ├── test_reproducibility.py
│       ├── test_negative_proof_presence.py
│       ├── test_policy_hash_lock.py
│       └── test_ajt_compliance.py
└── logs/                              # Output directory
```

---

## Why This Matters

### For Auditors
- **Reproducible**: Same inputs = same outputs, verifiable via hash
- **Traceable**: Every decision has explicit rule basis
- **Accountable**: Negative Proof shows what was prevented, not just what happened

### For Procurement
- **Risk Mitigation**: Demonstrates control over LLM output
- **Compliance**: Shows rule enforcement mechanism
- **Transparency**: Human-readable policy in YAML + machine-verifiable logs

### For Engineers
- **Local-first**: No API keys, no external dependencies
- **Fast**: Deterministic stub, no network calls
- **Testable**: Pytest-based validation suite

---

## License

MIT License

---

## Related Work

- **AJT Spec**: https://github.com/Nick-heo-eg/spec
- **OpenTelemetry Semantic Conventions**: https://opentelemetry.io/docs/specs/semconv/

---

**Feedback welcome** — especially from legal/compliance professionals who've dealt with AI audits.
