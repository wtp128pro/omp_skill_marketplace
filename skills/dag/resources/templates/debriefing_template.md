# Atomic Work Unit Debriefing: {{AWU_ID}} - {{TITLE}}

## 1. Execution Overview
- **AWU Identifier**: `{{AWU_ID}}`
- **Execution Status**: `{{STATUS_COMPLETED_OR_FAILED}}`
- **Completed At**: `{{TIMESTAMP}}`
- **Total Iterations Used**: `{{ITERATIONS_USED}}` of `{{MAX_ITERATIONS}}`
- **Maker Persona**: `{{MAKER_PERSONA}}` (Gemini 3.8 Flash High, OMP `agent: 'task'`; or Claude Opus 5.5 xhigh)
- **Checker Panelists**: 3 Distinct Auditors (Panelists 1 & 2: Gemini Pro Deep Think | Panelist 3: Claude Opus 5.5 xhigh)

---

## 2. Deliverables & Frame Condition Verification
### Created & Modified Deliverables (Write-Set W_u)
- `{{DELIVERABLE_1}}` (Diff: +{{ADDED_LINES}} / -{{REMOVED_LINES}})
- `{{DELIVERABLE_2}}`

### Frame Condition Audit (frame_condition_auditor.py)
- **Modifies Set Compliance**: VERIFIED (All writes contained within declared modifies set)
- **Immutable Path Invariance**: VERIFIED (Zero mutations to immutable files)
- **Unauthorized Side Effects**: NONE DETECTED

---

## 3. Post-Condition Verification Evidence
### Automated Test Proof
```text
{{TEST_RUNNER_STDOUT}}
```

### Invariant & Boundary Verification
- [x] Pre-condition check passed.
- [x] Post-condition check passed.
- [x] Code documentation complete with parameters and inline term explanations.

---

## 4. 3-Agent Adversarial Panel Adjudication
- **Panelist 1 (Correctness & Contract Falsifier)**: `{{PANELIST_1_VOTE}}`
  - Findings: `{{PANELIST_1_SUMMARY}}`
- **Panelist 2 (Security, Invariants & Boundary Auditor)**: `{{PANELIST_2_VOTE}}`
  - Findings: `{{PANELIST_2_SUMMARY}}`
- **Panelist 3 (Regression & Side-Effect Inquisitor)**: `{{PANELIST_3_VOTE}}`
  - Findings: `{{PANELIST_3_SUMMARY}}`

### Severity-Over-Majority Adjudication
- **Highest Active Defect Severity**: `{{HIGHEST_SEVERITY}}` (None / Sev-1 / Sev-2 / Sev-3)
- **Severity-Over-Majority Override Triggered**: `{{SEVERITY_OVERRIDE_FLAG}}`
- **Architectural Waivers Applied**: `{{WAIVERS_APPLIED_SUMMARY}}`
- **Final Adjudicated Verdict**: `{{FINAL_VERDICT}}` *(Approved / Approved with Waiver / Vetoed by Severity / Rejected by Majority)*

---

## 5. Captured Learnings & Operational Insights
- Permanent log written to disk: `learnings.jsonl`
- Operational Summary: `{{OPERATIONAL_LEARNINGS_SUMMARY}}`

---

## 6. DAG Impact & Unlocked Dependents
- Downstream nodes now unlocked for execution: `{{UNLOCKED_NODES_LIST}}`
