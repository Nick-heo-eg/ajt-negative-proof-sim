# AI Judgment Trail (AJT) — Negative Proof Simulation

**When an AI system blocks a risky answer, can you later prove it did?**

Most logs record *what an AI said*. This project records *what it refused to say, and why* — so that after an incident, you can show the dangerous options were caught on purpose, not by luck.

That evidence-of-what-was-blocked is what we call a **Negative Proof**.

> ⚠️ This is a **demonstration**, not a product. It uses synthetic data and a fake (deterministic) LLM so anyone can reproduce the exact same result. It does **not** make AI safer or guarantee compliance — it shows *how to keep auditable evidence of AI decisions*.

---

## The idea in one picture

```
User question
      │
      ▼
  AI generates 4 possible answers      ← (here: a deterministic stub, not a real LLM)
      │
      ▼
  Judgment Layer checks each answer    ← plain rules written in a YAML file
  against the policy
      │
      ├──►  3 answers violate the rules   →  BLOCKED  (each block is logged = Negative Proof)
      │
      └──►  1 answer passes all rules     →  ALLOWED  →  this is the final answer
      │
      ▼
  A signed log records everything:
  the chosen answer, the rules applied,
  every blocked answer + reason,
  and a hash so the run can be replayed.
```

**Core principle: the LLM *suggests*, the Judgment Layer *decides*.**

---

## Worked example: the Air Canada chatbot case

This is based on a [real, public incident](https://www.cbc.ca/news/canada/british-columbia/air-canada-chatbot-lawsuit-1.7116416) (*Moffatt v. Air Canada*) where an airline chatbot gave a customer wrong refund information — and a tribunal held the airline liable for it.

**The scenario:** a customer asks about bereavement-fare refunds. The AI might *hallucinate* that retroactive refunds are allowed (they aren't).

**The policy (3 rules, written in plain YAML):**

| Rule | What it blocks |
|------|----------------|
| **R1 — Source of truth** | Answers that contradict the official refund policy |
| **R2 — Citation required** | Answers with no reference to the official policy |
| **R3 — Confidence floor** | Answers the model isn't confident in (< 0.75) |

**What happens when you run it:**

- 4 candidate answers are generated
- **3 of them are blocked** (1 unsafe answer can break more than one rule, so this run logs **6 rule violations** in total)
- **1 answer passes** every rule → that one is served to the user → final decision: `allow`

So `allow` doesn't mean "anything goes." It means **the unsafe options were filtered out first, and only the clean one survived** — and you have a log proving it.

---

## Try it yourself (30 seconds)

```bash
pip install -r requirements.txt

# Run the simulation
PYTHONPATH=. python -m sim.run --case aircanada --seed 42 --out logs/demo.json
```

Expected output:

```
✓ Simulation complete: aircanada
  Policy:        1.0.0 (960abe31...)
  Candidates:    4
  Negative Proofs: 6      ← rule violations recorded
  Final Decision: allow   ← the one clean answer
  Run Hash:      82960705...
```

Run it again with the same seed → you get the **exact same hash**. That reproducibility is the whole point: an auditor can re-run your decision and confirm nothing was changed.

```bash
pytest -v   # 22 tests
```

---

## What's in the log

Every run writes one JSON file containing:

- **All candidates** — every answer the AI considered
- **The decision** — which answer was chosen + which rules were applied
- **Negative Proof** — each blocked answer and the reason it was blocked
- **AJT record** — the spec-compliant trail (9 required fields)
- **Reproducibility** — seed + policy hash + run hash

---

## What this is — and isn't

| ✅ This project demonstrates | ❌ This project does NOT claim |
|------------------------------|-------------------------------|
| Auditable decision boundaries via structured logs | That the AI's answers are *correct* |
| Reproducible trails for after-the-fact review | Legal compliance |
| Clean separation of AI generation from rule enforcement | Safety or harm prevention |

It's a **rehearsal for an audit**, not a compliance tool. All policies, cases, and inputs are **synthetic**.

---

## Design principles

1. **Fail closed** — if logging fails, no decision is emitted (silence is never an option)
2. **No silent failures** — every block and every error is written down explicitly
3. **Log, don't enforce** — this is an audit trail, not a runtime policy engine

---

## Why it matters

- **For auditors** — same inputs always produce the same output, verifiable by hash; every decision has an explicit rule basis.
- **For procurement / risk** — demonstrates concrete control over LLM output, in human-readable YAML + machine-verifiable logs.
- **For engineers** — local-first, no API keys, no network calls, fully tested.

> Curious why existing tools (CloudTrail, S3, Datadog) aren't enough?
> 👉 **[Why AJT? When "what happened" isn't enough](WHY_AJT.md)**

---

## Project layout

```
ajt-negative-proof-sim/
├── sim/
│   ├── run.py                      # CLI entry point
│   ├── core/
│   │   ├── candidate_generator.py  # Deterministic LLM stub
│   │   ├── judgment_layer.py       # Rule application engine
│   │   ├── ajt_record.py           # AJT spec implementation
│   │   ├── log_schema.py           # Pydantic models
│   │   └── hash_utils.py           # SHA256 hashing
│   ├── cases/aircanada_case.py     # The Air Canada case
│   ├── policies/policy_aircanada.yaml
│   ├── fixtures/aircanada_inputs.json
│   └── tests/                      # reproducibility, negative proof, hash lock, spec compliance
└── logs/                           # output directory
```

---

## Relation to the AJT Spec

This simulation uses the minimal Judgment Trace schema from the public spec:
**https://github.com/Nick-heo-eg/spec**

- The spec is used **as-is** — no modifications or extensions proposed
- Negative Proof is built as an **optional extension layer** on top
- This repo depends only on the public spec and is decoupled from any internal systems

*Note: the schema is named "Judgment Trace" for historical reasons; the concept is the AI Judgment Trail.*

---

## License

MIT

## Related work

- **AJT Spec** — https://github.com/Nick-heo-eg/spec
- **OpenTelemetry Semantic Conventions** — https://opentelemetry.io/docs/specs/semconv/

---

**Feedback welcome** — especially from legal and compliance professionals who've dealt with AI audits.
