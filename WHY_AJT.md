# Why AJT? When "what happened" isn't enough.

## TL;DR

**Now (2026)**: AWS S3 + CloudTrail + Datadog = EU AI Act compliant ✅

**After incident**: Court asks "why was this allowed?" = Existing stack can't answer immediately ❌

**AJT**: Bridges this gap by logging judgment context in one line.

---

## Current Stack is Enough... Until It Isn't

### ✅ What existing tools cover (peacetime audit)

| Tool | What it logs | Article 12 compliance |
|------|-------------|----------------------|
| CloudTrail | API calls, timestamps, users | ✅ Traceability |
| S3 Object Lock | Immutable storage | ✅ Tamper-resistant |
| Datadog | Events, metrics | ✅ Monitoring |

**Result**: Most companies pass audits with this stack in 2026.

---

### ❌ What's missing (post-incident investigation)

**Question shifts from:**
```
"What happened?"  →  "Why was this decision allowed at that moment?"
```

**Existing logs answer:**
- ✅ When was the API called?
- ✅ Who called it?
- ✅ Which model was used?

**But can't immediately answer:**
- ❌ Why was this judgment made?
- ❌ What was the policy version?
- ❌ How was risk classified?
- ❌ Was there human oversight?
- ❌ Were safer alternatives blocked?

**Time to reconstruct**: Days to weeks (scattered logs)

---

## AJT: Judgment Context in One Line

```json
{
  "timestamp": "2026-01-15T14:32:11Z",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "gpt-4",
  "decision": "allow",
  "risk_level": "low",
  "human_in_loop": false,
  "policy_version": "v2.3.1",
  "app_version": "1.0.5",
  "session_id": "user-session-abc123"
}
```

**Reconstruction time**: Immediate (single log line)

---

## Real-World Scenario

### Air Canada Chatbot Case (2024)

**What happened:**
- Chatbot gave wrong bereavement refund advice
- Customer relied on it
- Tribunal ruled airline liable

**Post-incident questions:**
- Were safer responses generated and blocked?
- Did filtering rules run correctly?
- Was this a control failure or just bad luck?

**With CloudTrail only:**
> "We can show the API call happened, but reconstructing the decision context requires correlating multiple log sources. This will take 2-3 weeks."

**With AJT:**
> "Here's the exact log line showing: model used, risk assessment, policy version, and whether human review occurred. Reconstruction complete."

---

## When Does This Matter?

### Now (2026 Q1)
- ✅ Existing stack passes audits
- ⚠️ AJT is **optional** (defense-in-depth)

### After first major incident (2026-2027 predicted)
- ⚠️ Courts demand immediate judgment reconstruction
- ⚠️ "We had policies" → "Prove they ran correctly"
- ✅ AJT becomes **essential** for liability defense

### EU AI Office guidance update (2026 Q2 expected)
- Potential strengthening of "operational reconstruction" requirements
- Emphasis on "judgment trail" not just "event log"

---

## Positioning

**Current message:**
> "Do you need AJT right now? No, existing stack works.
> Should you prepare before an incident? That's the question."

**Value proposition:**
```
Existing stack: "Incident log"  → Explains what, struggles with why
AJT:           "Judgment log" → Proves why decisions were allowed
```

**ROI:**
- **Cost now**: ~1KB per AI call (negligible)
- **Cost without it after incident**: Weeks of log reconstruction, weaker liability defense
- **Insurance value**: Verifiable accountability when it matters most

---

## FAQ

**Q: Isn't this over-engineering?**
A: For peacetime audits, yes. For post-incident legal defense, no.

**Q: When would I actually need this?**
A: When "what did the AI say" becomes "why did you allow it to say that."

**Q: Can't I add this after an incident?**
A: No - you need logs from the moment the decision was made.

---

## Related

- EU AI Act Article 12: Record-keeping requirements
- Air Canada v. Moffatt (2024): Chatbot liability case
- GDPR Article 22: Automated decision-making

---

**Bottom line**: AJT is optional insurance. Cheap now, invaluable after an incident.
