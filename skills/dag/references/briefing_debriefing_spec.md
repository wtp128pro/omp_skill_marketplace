# Briefing, Verification & Debriefing Formal Specification

## 1. Overview & On-Disk Auditability Standard

To guarantee complete transparency, reproducibility, and auditability, every Atomic Work Unit (AWU) MUST maintain **four formal on-disk artifacts**:
1. **`briefing.md`**: The pre-execution contract given to the Maker subagent.
2. **`panel_verdicts.md`**: The 3-agent adversarial verification panel findings and Severity-Over-Majority matrix.
3. **`learnings.jsonl`**: The on-disk structured self-learning log capturing defect counterexamples, root causes, and negative constraints.
4. **`debriefing.md`**: The post-execution deliverable summary, invariant verification proofs, and unlocked dependents.

All four files reside in `.omp_wip/<session>/units/<AWU-ID>_<slug>/` and are automatically scaffolded via:
```bash
python3 ~/.omp/agent/skills/dag/scripts/scaffold_dag_unit.py --unit-id "<AWU-ID>" --slug "<slug>" --title "<Title>" --maker-persona "<Persona>"
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/scaffold_dag_unit.sh --unit-id "<AWU-ID>" --slug "<slug>" --title "<Title>" --maker-persona "<Persona>"
```

---

## 2. Formal Briefing Specification (`briefing.md`)

The briefing is a binding contract. The Maker subagent (`Model: 'flash'`) is evaluated against its contents.

### Required Briefing Fields & Structure:
```markdown
# AWU Briefing: [AWU-ID] - [Title]

## 1. Execution Metadata
- **AWU Identifier**: AWU-001
- **Task Moniker**: auth-refactor
- **Assigned Maker Persona**: Principal Systems Programmer
- **Assigned Model Tier / Agent**: Gemini 3.8 Flash High / Primary Tier (OMP `agent: 'task'`; or Claude Opus 5.5 xhigh for architectural units)
- **Mandatory Verification**: Heterogeneous 3-Agent Adversarial Panel (Gemini Pro Deep Think & Claude Opus 5.5 xhigh) with active Self-Learning Loop
- **Iteration Index**: 1 of 3
- **Prerequisite Units**: [List of completed prerequisite AWUs or None]

## 2. Objective & Mission Statement
A concise, formal description of the exact functional goal.

## 3. Strict Scope Boundaries
- **IN-SCOPE**: Explicitly itemized list of tasks, files, and functions to create or modify.
- **OUT-OF-SCOPE (Anti-Goldplating & Anti-Drift)**: Explicitly forbidden features, refactorings, or cosmetic additions.

## 4. Input Specifications & Reputable Sources
- **Source Inputs**: Exact file paths, schemas, and configurations consumed.
- **Authoritative Citations**: Primary standards, RFCs, or documentation URLs used to validate inputs.

## 5. Formal System Pre-Conditions & Post-Conditions
- **Pre-Conditions**: State that must be true prior to execution.
- **Post-Conditions**: State that must be strictly guaranteed upon completion.

## 6. System Invariants & Non-Negotiables
Unbroken rules cataloged during Cartography that must remain inviolate.

## 7. Mandatory Accumulated Learnings & Negative Constraints (For Iterations > 1)
Structured negative constraints extracted from `learnings.jsonl` following previous panel rejections.

## 8. Acceptance & Verification Criteria
Specific test commands, assertions, docstrings, and verification criteria required to pass.
```

---

## 3. 3-Agent Adversarial Panel Findings Specification (`panel_verdicts.md`)

Records the independent scrutiny of 3 heterogeneous adversarial panelists:
- **Panelist 1**: Correctness & Contract Boundary Falsifier (Gemini Pro Deep Think, OMP `agent: 'reviewer'`).
- **Panelist 2**: Security, Invariants & Resource Exhaustion Auditor (Gemini Pro Deep Think, OMP `agent: 'security-reviewer'`).
- **Panelist 3**: Regression, Blast Radius & Systemic Sentinel (Claude Opus 5.5 xhigh, OMP `agent: 'reviewer'`).

Includes the Severity-Over-Majority adjudication matrix computed via `~/.omp/agent/skills/dag/scripts/adjudicate_panel.py` (or `~/.omp/agent/skills/dag/scripts/adjudicate_panel.sh`).

---

## 4. Formal Debriefing Specification (`debriefing.md`)

The debriefing is the permanent record of what was created, tested, and approved.

### Required Debriefing Fields & Structure:
```markdown
# AWU Debriefing: [AWU-ID] - [Title]

## 1. Execution Summary
- **AWU Identifier**: AWU-001
- **Final Status**: COMPLETED (or FAILED)
- **Completed At**: 2026-09-20T01:35:00Z
- **Iterations Required**: 1 of 3
- **Maker Persona**: Principal Systems Programmer (Gemini 3.8 Flash High, agent: 'task'; or Claude Opus 5.5 xhigh)
- **Checker Panelists**: 3 Distinct Auditors (Panelists 1 & 2: Gemini Pro Deep Think | Panelist 3: Claude Opus 5.5 xhigh)

## 2. Deliverables & Modified Artifacts
- List of created files with relative paths and line counts.
- Summary of modified files with unified diff summaries.

## 3. Post-Condition Verification Evidence
- Exact test execution commands run.
- Test stdout/stderr outputs showing all assertions passed.
- Proof of invariant compliance.

## 4. 3-Agent Adversarial Panel Review Findings
- **Panelist 1 (Correctness & Contract Falsifier)**: [APPROVE / REJECT] - Summary of findings.
- **Panelist 2 (Security & Invariants Auditor)**: [APPROVE / REJECT] - Summary of findings.
- **Panelist 3 (Regression & Side-Effect Inquisitor)**: [APPROVE / REJECT] - Summary of findings.
- **Highest Defect Severity**: [None / Sev-1 / Sev-2 / Sev-3]
- **Severity-Over-Majority Override Triggered**: [YES / NO]
- **Adjudicated Verdict**: [PASS / REJECT_VETO / REJECT_MAJORITY]

## 5. Captured Learnings & Operational Insights
Operational summary and link to disk log `learnings.jsonl`.

## 6. DAG Impact & Unlocked Dependents
- Enumeration of downstream DAG nodes unlocked by this unit's completion.
```
