# Complete DAG Execution Walkthrough: `auth-token-engine`

This reference example illustrates the execution of a project using the `dag` skill, demonstrating cartography, decomposition, Maker!=Checker execution, an adversarial Sev-1 veto, self-learning extraction, and final regression verification.

---

## Step 1: Session Initialization
The session is initialized in `.omp_wip`:
```bash
python3 ~/.omp/agent/skills/dag/scripts/init_dag_session.py --task-moniker "auth-token-engine"
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/init_dag_session.sh --task-moniker "auth-token-engine"
```
Created: `.omp_wip/2026-09-20_01-15-00_auth-token-engine/`

---

## Step 2: Cartography & Input Gap Analysis
The Cartographer scans the repository and authoritative standards:
- **Authoritative Source Cited**: [RFC 7519 - JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519) Section 4.1.4 (`exp` claim numeric epoch handling).
- **Gap Identified**: User request specified "tokens expire", but did not define clock skew tolerance.
- **Resolution**: Grounded in standard practice: bounded clock skew tolerance set to 60 seconds with strict unit test coverage.
- Deliverables written to:
  - `.omp_wip/2026-09-20_01-15-00_auth-token-engine/00_cartography/cartography_report.md`
  - `.omp_wip/2026-09-20_01-15-00_auth-token-engine/00_cartography/input_gap_analysis.md`

---

## Step 3: DAG Formulation
The task is decomposed into atomic units:
1. `AWU-001`: Crypto Token Primitives (Maker: `PrincipalSystemsMaker`)
2. `AWU-002`: Session Cache Adapter (Maker: `DistributedStorageSpecialist`, depends on `AWU-001`)
3. `AWU-003`: HTTP Authentication Middleware (Maker: `TypeSafeApiArchitect`, depends on `AWU-001`, `AWU-002`)

Validated with:
```bash
python3 ~/.omp/agent/skills/dag/scripts/validate_dag.py --manifest-path .omp_wip/2026-09-20_01-15-00_auth-token-engine/01_dag/dag_manifest.json
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/validate_dag.sh --manifest-path .omp_wip/2026-09-20_01-15-00_auth-token-engine/01_dag/dag_manifest.json
```

---

## Step 4: AWU-001 Iteration 1 & The Adversarial Veto

### 1. Unit Scaffolding & Formal Briefing
The orchestrator scaffolds the unit with all required contracts and self-learning log:
```bash
python3 ~/.omp/agent/skills/dag/scripts/scaffold_dag_unit.py --unit-id "AWU-001" --slug "crypto-primitives" --title "Implement Crypto Token Primitives" --maker-persona "PrincipalSystemsMaker"
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/scaffold_dag_unit.sh --unit-id "AWU-001" --slug "crypto-primitives" --title "Implement Crypto Token Primitives" --maker-persona "PrincipalSystemsMaker"
```
`.omp_wip/.../units/AWU-001_crypto-primitives/briefing.md` specifies pre-conditions, post-conditions, and assigned model **Gemini 3.8 Flash High** (OMP `agent: 'task'`).

### 2. Maker Execution
Maker implements `verifyToken()` using Gemini 3.8 Flash High.

### 3. Parallel 3-Agent Adversarial Panel (Tri-Model Heterogeneous Verification)
The orchestrator launches all 3 checkers concurrently in a single OMP `task` batch call (or `eval` workpool) with prompts from `resources/templates/panel_prompt.md`:
- **Panelist 1 (Correctness & Contract Falsifier - Gemini Pro Deep Think)**: Discovers that passing `{"alg": "none"}` passes verification because the algorithm check was permissive. Severity: **Sev-1 (Critical Security Vulnerability)**.
- **Panelist 2 (Security Auditor - Gemini Pro Deep Think)**: Flags potential timing attack on signature comparison. Severity: **Sev-2 (Major)**.
- **Panelist 3 (Systemic Sentinel - Claude Opus 5.5 xhigh)**: Cross-vendor audit discovers that altering token payload serialization silently breaks downstream auth callers expecting raw hex strings. Severity: **Sev-2 (Major Regression)** — exercising its cross-vendor unilateral veto authority.
Findings are recorded into `panel_verdicts.md`.

### 4. Automated Adjudication: Severity Over Majority
The orchestrator runs `adjudicate_panel`:
```bash
python3 ~/.omp/agent/skills/dag/scripts/adjudicate_panel.py --unit-id "AWU-001"
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/adjudicate_panel.sh --unit-id "AWU-001"
```
- Vote count: 1 Approve, 2 Reject.
- Highest Severity: **Sev-1 (Critical)**.
- **Verdict**: **REJECT_VETO (VETOED BY SEVERITY)**.
- Severity Over Majority automatically triggers a veto.

### 5. Self-Learning Capture (`learnings.jsonl`)
The engine automatically logs the structured failure to `units/AWU-001_crypto-primitives/learnings.jsonl`:
```json
{
  "awu_id": "AWU-001",
  "iteration": 1,
  "timestamp": "2026-09-20T01:25:30Z",
  "severity": "Sev-1",
  "defect_summary": "Algorithm confusion vulnerability in token header verification",
  "root_cause": "Permissive algorithm header allowed algorithm confusion ('none' attack).",
  "negative_constraint": "DO NOT allow dynamic algorithm headers. MUST enforce hardcoded HMAC-SHA256 and constant-time signature comparison."
}
```

---

## Step 5: AWU-001 Iteration 2 (Remediation & Pass)

1. Updated `briefing.md` generated with accumulated negative constraints formatted by `adjudicate_panel`.
2. Maker fixes the vulnerability, using `crypto.timingSafeEqual()` and strict algorithm pinning.
3. 3-Agent Panel re-evaluates in parallel:
   - Panelist 1: **APPROVE** (Verified 'none' attack is blocked).
   - Panelist 2: **APPROVE** (Verified constant-time comparison).
   - Panelist 3: **APPROVE** (Full docstrings and parameter descriptions verified).
4. Automated Adjudication: **PASS** (Zero Sev-1/Sev-2, 3/3 Approvals). Status in `dag_manifest.json` set to `COMPLETED`.
5. Formal `debriefing.md` signed and recorded. Downstream `AWU-002` unlocked!

---

## Step 6: On-Disk Audit & Phase 5 Global Regression Audit
Before closing the session:
1. Validate on-disk auditability:
   ```bash
python3 ~/.omp/agent/skills/dag/scripts/validate_dag.py --audit-disk
# Or using the shell wrapper:
~/.omp/agent/skills/dag/scripts/validate_dag.sh --audit-disk
   ```
   Confirms all unit folders, briefings, panel verdicts, and `learnings.jsonl` are present on disk.
2. The Phase 5 panel audits the global git diff across the entire repository to ensure zero inadvertent negative side effects:
   - Deliverable: `.omp_wip/.../99_final_review/adversarial_regression_audit.md`.
   - Result: Clean approval.

---

## Step 7: Socratic Human Presentation
The orchestrator reports the completion to the user in plain human language, with every term explained inline:
> "We completed the authentication engine using our DAG (a Directed Acyclic Graph, which is a step-by-step roadmap where each task moves forward without looping). During adversarial testing, our verification panel caught an algorithm confusion bug (a security flaw where an attacker tricks the system into accepting unverified tokens). The issue was immediately fixed, verified with constant-time cryptographic checks (a timing defense that prevents attackers from guessing secret keys based on response speed), and confirmed across all tests."
