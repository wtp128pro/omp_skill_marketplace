# 3-Agent Adversarial Verification Panel Protocol

## 1. Core Mission & Adversarial Philosophy

The 3-Agent Adversarial Verification Panel exists to rigorously falsify and stress-test every artifact produced by a Maker before it is admitted into the project history. The default posture of each panelist is **skeptical, hostile, and uncompromising**.

---

## 2. Panelist Roles & Verification Mandates

```text
┌────────────────────────────────────────────────────────────────────────┐
│             TRI-MODEL HETEROGENEOUS ADVERSARIAL PANEL STRUCTURE        │
├────────────────────────────────────────────────────────────────────────┤
│ Panelist 1: Correctness & Contract Falsifier                           │
│   Model Tier: Gemini Pro Deep Think (Deep Analytical Reasoning)        │
│   Focus: Mathematical correctness, edge cases, pre/post-conditions    │
├────────────────────────────────────────────────────────────────────────┤
│ Panelist 2: Security, Invariants & Boundary Auditor                    │
│   Model Tier: Gemini Pro Deep Think (Deep Vulnerability & Exploit)     │
│   Focus: Exploit vectors, race conditions, memory leaks, invariants    │
├────────────────────────────────────────────────────────────────────────┤
│ Panelist 3: Regression, Blast Radius & Systemic Sentinel               │
│   Model Tier: Claude Opus 5.5 xhigh (Macro-Architectural Reasoning)    │
│   Focus: Downstream callers, ABI/API stability, cross-vendor veto      │
└────────────────────────────────────────────────────────────────────────┘

### Panelist 1: Correctness & Contract Falsifier (Gemini Pro Deep Think)
- Evaluates whether the implementation satisfies the formal `briefing.md` contract.
- Crafts boundary edge cases: zero values, empty collections, maximum integer values, malformed Unicode, unexpected file termination.
- Proves mathematically or logically that the post-conditions hold across all legal input states.

### Panelist 2: Security, Invariants & Boundary Auditor (Gemini Pro Deep Think)
- Audits for common vulnerability classes: injection, buffer overflow, uncontrolled recursion, unhandled promise rejections, race conditions.
- Validates system invariants cataloged during Cartography: transactional integrity, thread safety, sanitization.
- Assesses resource consumption: unbounded memory growth, file descriptor leaks, CPU spin-loops.

### Panelist 3: Regression, Blast Radius & Systemic Sentinel (Claude Opus 5.5 xhigh)
- **Cross-Vendor Adversarial Auditor**: Scrutinizes code authored by Google Gemini from an entirely orthogonal Anthropic foundation, neutralizing vendor-family cognitive blind spots.
- Audits the full multi-file blast radius: Does this change alter the subtle runtime behavior of existing callers?
- Checks backward compatibility, exported signature stability, and system invariants.
- Searches for insidious side effects: unexpected disk writes, mutated shared state, configuration drift, or unrequested architectural goldplating.
- Holds **unilateral veto authority** under Severity-Over-Majority if any Sev-1 or Sev-2 flaw is discovered.

### 2.1 The Value of Cross-Vendor Epistemic Orthogonality
In single-vendor verification pipelines, models share tokenizer quirks, RLHF alignment assumptions, and training-set blind spots. A failure mode that slips past a Gemini maker may also slip past a Gemini checker. Introducing **Claude Opus 5.5 xhigh** as Panelist 3 breaks this symmetry:
1. Different model architecture and attention mechanisms.
2. Distinct pre-training corpus and safety tuning.
3. Unrivaled macro-architectural synthesis and code comprehension at scale.
---

## 3. Defect Classification & Severity Hierarchy

Every issue uncovered by a panelist must be classified into one of three standardized severities:

| Severity Level | Definition & Criteria | Examples |
| :--- | :--- | :--- |
| **Sev-1 (Critical)** | Catastrophic flaw compromising system stability, security, or data integrity. Invariant breach. | Arbitrary code execution, SQL injection, silent data corruption, deadlock in core worker, memory leak in hot loop. |
| **Sev-2 (Major)** | Functional failure violating a briefing post-condition or breaking an existing contract/caller. Missing required docs or tests. | Unhandled null pointer on legal edge case, incorrect math calculation, missing parameter validation, undocumented public function. |
| **Sev-3 (Minor)** | Non-blocking suggestion, minor stylistic variance, naming improvement, or non-critical doc refinement. | Typo in internal comment, slightly verbose loop structure, non-blocking test optimization. |

---

## 4. The Golden Adjudication Rule: Severity Over Majority & Cryptographic Waivers

In standard voting bodies, a 2-to-1 vote constitutes a passing majority. **In the `dag` engine, democratic voting is rejected as mathematically unsound.**

> [!CAUTION]
> ### The Severity-Over-Majority Axiom
> **The gravity of a defect strictly supersedes numerical votes.**
> If **ANY** panelist discovers an un-waived **Sev-1 (Critical)** or **Sev-2 (Major)** defect, the work unit is **IMMEDIATELY REJECTED / VETOED**, even if the other two panelists voted `APPROVE`.

### 4.1 The Cryptographic Waiver Protocol
To prevent catastrophic blind-spots while permitting governed business trade-offs:
1. **Sev-1 Defects (Fatal Vulnerabilities / Data Loss Hazards)**: *Structurally Unwaivable*. Must be refactored; zero exceptions.
2. **Sev-2 Defects (Major Architectural / Contract Flaws)**: May be overridden IF AND ONLY IF an authorized human Principal Systems Architect attaches a valid cryptographic/architectural waiver to `waivers.json`:
   $$\mathcal{W} = \langle \text{DefectID}, \text{ArchitectID}, \text{MitigationRationale}, \text{ExpirationEpoch}, \text{Signature} \rangle$$
3. **Mandatory Falsification Proof Requirement ($\text{Proof}(d)$)**:
   Any defect logged by an adversarial auditor must provide:
   $$\text{Proof}(d) = \langle \text{InputPayload}, \text{ExecutionTrace}, \text{ViolatedInvariant}, \text{CounterexampleData} \rangle$$

### Verdict Resolution Table:

| Panelist 1 | Panelist 2 | Panelist 3 | Highest Severity Found | Waiver Status | Final Verdict | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| APPROVE | APPROVE | APPROVE | None (or Sev-3) | N/A | **PASS** | Write debriefing and unlock dependents. |
| APPROVE | APPROVE | REJECT | **Sev-1 (Critical)** | Unwaivable | **REJECT (VETO)** | Loop back to Maker with Sev-1 learnings. |
| APPROVE | APPROVE | REJECT | **Sev-2 (Major)** | No Waiver | **REJECT (VETO)** | Loop back to Maker with Sev-2 learnings. |
| APPROVE | APPROVE | REJECT | **Sev-2 (Major)** | Valid Waiver $\mathcal{W}$ | **PASS_WAIVED** | Log architectural waiver in debriefing; pass unit. |
| APPROVE | APPROVE | REJECT | **Sev-3 (Minor)** | N/A | **PASS_WITH_CAVEAT**| Log Sev-3 note in debriefing; pass unit. |
| REJECT | REJECT | APPROVE | Any | N/A | **REJECT_MAJORITY** | Loop back to Maker with consolidated learnings. |

### 4.2 Automated Adjudication Engine (`fdag adjudicate`)
To eliminate human or LLM bias when evaluating votes, the orchestrator executes `fdag adjudicate`:
```bash
fdag adjudicate --unit-id "AWU-001"
# Or using python script:
python3 ~/.omp/agent/skills/dag/scripts/adjudicate_panel.py --unit-id "AWU-001"
```
The script:
1. Evaluates all 3 panelist votes and defect severities recorded in `panel_verdicts.json`.
2. Validates mandatory counterexamples ($\text{Proof}(d)$) and anti-rubber-stamping evidence.
3. Evaluates attached waivers in `waivers.json` or inline verdicts.
4. Automatically triggers `REJECT_VETO` if any active Sev-1 or un-waived Sev-2 defect is present.
5. Automatically writes structured counterexamples and negative constraints to `learnings.jsonl`.
6. Atomically updates `dag_manifest.json` status and injects negative constraints into `briefing.md` for iteration $N+1$.
### 4.3 Standard Adversarial Prompts & Readiness Scorecard (`fdag scorecard`)
All 3 panelist subagents are instantiated using standardized prompt contracts found in [Panel Prompts Template](../resources/templates/panel_prompt.md), enforcing the Two-Plane Structural Envelope and guaranteeing compliance with the 5-Point Enterprise Invariant Readiness Scorecard (`fdag scorecard`).

---

## 5. Phase 5: Final Global Adversarial Analysis

Before completing any task that modified or added code, a **final holistic 3-agent adversarial panel** convenes in Phase 5:

1. **Mission**: Ensure that the accumulated changes across all AWUs do not cause inadvertent negative side effects to the project as a whole.
2. **Review Canvas**: The full git diff, entire test suite results, and system integration points.
3. **Panelist Specializations & Model Tiering**:
   - *Panelist A (System Blast Radius Auditor)*: **Claude Opus 5.5 xhigh** (`anthropic/claude-opus-5-5:xhigh`, `agent: 'reviewer'`) verifies non-touched subsystems continue to function identically and backward compatibility remains intact.
   - *Panelist B (Performance & Scalability Sentinel)*: **Gemini Pro Deep Think** (`google-antigravity/gemini-3-pro:high`, `agent: 'security-reviewer'`) audits for hidden latency regressions, connection pool exhaustion, memory growth, or I/O bottlenecks.
   - *Panelist C (Codebase Architectural Sentinel)*: **Claude Opus 5.5 xhigh** (`anthropic/claude-opus-5-5:xhigh`, `agent: 'reviewer'`) verifies adherence to project conventions, documentation standards, and clean dependency boundaries.
4. **Deliverable**: `.omp_wip/<session>/99_final_review/adversarial_regression_audit.md`.

### 5.1 On-Disk Audit Verification
Before closing the session, run:
```bash
python3 ~/.omp/agent/skills/dag/scripts/validate_dag.py --audit-disk
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/validate_dag.sh --audit-disk
```
This mathematically proves that every completed AWU has an on-disk `briefing.md`, `panel_verdicts.md` with 3 checker signoffs, `learnings.jsonl`, and `debriefing.md` without unaddressed Sev-1 or Sev-2 violations.
