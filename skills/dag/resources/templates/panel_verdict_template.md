# 3-Agent Adversarial Verification Panel Findings

**Target AWU**: `{{AWU_ID}}` - `{{TITLE}}`  
**Evaluation Timestamp**: `{{TIMESTAMP}}`  
**Panelist Model Tiers**: Heterogeneous Triad (Panelists 1 & 2: Gemini Pro Deep Think | Panelist 3: Claude Opus 5.5 xhigh)

---

## Panelist 1: Correctness & Contract Falsifier
- **Assigned Auditor Persona**: Mathematical & Contract Boundary Inquisitor
- **Vote**: `{{PANELIST_1_VOTE}}` *(APPROVE / REJECT)*
- **Highest Defect Severity Detected**: `{{PANELIST_1_SEVERITY}}` *(None / Sev-1 / Sev-2 / Sev-3)*
- **Adversarial Assessment**:
  - Verification of pre/post-conditions: `{{ASSESSMENT_1_CONDITIONS}}`
  - Edge case & boundary probing results: `{{ASSESSMENT_1_EDGE_CASES}}`
  - Counterexamples discovered (if any): `{{ASSESSMENT_1_COUNTEREXAMPLES}}`

---

## Panelist 2: Security, Invariants & Boundary Auditor
- **Assigned Auditor Persona**: Security & Invariant Integrity Sentinel
- **Vote**: `{{PANELIST_2_VOTE}}` *(APPROVE / REJECT)*
- **Highest Defect Severity Detected**: `{{PANELIST_2_SEVERITY}}` *(None / Sev-1 / Sev-2 / Sev-3)*
- **Adversarial Assessment**:
  - Exploit & vulnerability scan: `{{ASSESSMENT_2_SECURITY}}`
  - Invariant preservation audit: `{{ASSESSMENT_2_INVARIANTS}}`
  - Resource leakage & concurrency hazards: `{{ASSESSMENT_2_RESOURCES}}`

---

## Panelist 3: Regression, Blast Radius & Systemic Sentinel (Claude Opus 5.5 xhigh)
- **Assigned Auditor Persona**: Systemic Invariants & Blast Radius Inquisitor (Cross-Vendor Veto Sentinel)
- **Vote**: `{{PANELIST_3_VOTE}}` *(APPROVE / REJECT)*
- **Highest Defect Severity Detected**: `{{PANELIST_3_SEVERITY}}` *(None / Sev-1 / Sev-2 / Sev-3)*
- **Adversarial Assessment**:
  - Upstream/Downstream caller impact: `{{ASSESSMENT_3_CALLERS}}`
  - Unintended state mutations / side effects: `{{ASSESSMENT_3_SIDE_EFFECTS}}`
  - Code documentation & inline term compliance: `{{ASSESSMENT_3_DOCS}}`

---

## Panel Adjudication Matrix (Severity Over Majority)

| Criterion | Value |
| :--- | :--- |
| **Numerical Votes** | `{{COUNT_APPROVE}}` Approve / `{{COUNT_REJECT}}` Reject |
| **Global Highest Severity** | `{{HIGHEST_GLOBAL_SEVERITY}}` *(None / Sev-1 / Sev-2 / Sev-3)* |
| **Severity-Over-Majority Triggered?** | `{{SEVERITY_OVERRIDE_FLAG}}` *(YES/NO)* |
| **FINAL ADJUDICATED VERDICT** | `{{FINAL_VERDICT}}` *(PASS / PASS_WITH_CAVEAT / REJECT_VETO / REJECT_MAJORITY)* |

### Adjudication Rationale & Self-Learning Action
`{{FINAL_ADJUDICATION_EXPLANATION}}`

- **Iteration Index**: `{{ITERATION_INDEX}}` of `{{MAX_ITERATIONS}}`
- **Logged to Disk**: `learnings.jsonl`
- **Negative Constraints Captured**: `{{NEGATIVE_CONSTRAINTS_SUMMARY}}`
