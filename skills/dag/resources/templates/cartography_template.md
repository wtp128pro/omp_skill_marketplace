# Cartography & System Architecture Report

## 1. Executive Summary
- **Session Moniker**: `{{TASK_MONIKER}}`
- **Generated At**: `{{TIMESTAMP}}`
- **Lead Cartographer**: Systems Architecture Reconnaissance Agent
- **Readiness Gate Status**: `{{READINESS_SCORECARD_STATUS}}`

---

## 2. Static Codebase Topology
- **Root Directory**: `{{ROOT_PATH}}`
- **Primary Technology Stack**: `{{STACK_DETAILS}}`
- **Build / Packaging Toolchain**: `{{BUILD_TOOLS}}`
- **Test Frameworks**: `{{TEST_FRAMEWORKS}}`

### File & Directory Map
```text
{{DIRECTORY_TREE}}
```

---

## 3. Core Interface & Schema Catalog
| Interface / Contract | File Location | Public Functions / Endpoints | Inputs / Outputs |
| :--- | :--- | :--- | :--- |
| `{{INTERFACE_1}}` | `{{PATH_1}}` | `{{FUNCTIONS_1}}` | `{{TYPES_1}}` |
| `{{INTERFACE_2}}` | `{{PATH_2}}` | `{{FUNCTIONS_2}}` | `{{TYPES_2}}` |

---

## 4. Invariant Catalog (Non-Negotiable System Rules)
1. **Invariant 1**: `{{INVARIANT_1_DESCRIPTION}}`
2. **Invariant 2**: `{{INVARIANT_2_DESCRIPTION}}`
3. **Invariant 3**: `{{INVARIANT_3_DESCRIPTION}}`

---

## 5. Input Gap Analysis (IGA) & Plausibility Trap Defense
*Mechanistic Grounding: Unconstrained LLMs smooth over missing parameters by sampling median tutorial completions from pretraining. All input specifications must be classified across the 3 formal input gap classes prior to AWU decomposition.*

### 5.1 Three-Class Input Gap Audit Table
| Gap Class | Parameter / Surface | Status | Reputable Source Citation | Resolution & Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| **Class 1 (Sev-1)**: Unstated Invariants / Bounds | `{{PARAM_C1}}` | RESOLVED | `{{CITATION_1_URL}}` | Bounded by explicit pre-condition. |
| **Class 2 (Sev-2)**: Contractual Ambiguities | `{{PARAM_C2}}` | RESOLVED | `{{CITATION_2_URL}}` | Typed schema and error enums specified. |
| **Class 3 (Sev-1)**: Partial Failure / Timeouts | `{{PARAM_C3}}` | RESOLVED | `{{CITATION_3_URL}}` | Decoupled via transactional outbox & TTL lease. |

### 5.2 Plausibility Trap Veto Audit
- [ ] Concurrency Isolation: Explicit database transaction level and pessimistic locking (`SELECT ... FOR UPDATE`) declared.
- [ ] Distributed Fencing: Monotonically increasing fencing tokens defined for all distributed locks.
- [ ] Timeout & Retry Storm Defenses: Maximum latency SLA and backoff jitter bounded for all external calls.
- [ ] Zero Assumptions Rule: All external dependencies grounded in authoritative RFCs or vendor documentation.

---

## 6. Blast Radius & Failure Mode Analysis
- **Maximum Expected Blast Radius**: `{{BLAST_RADIUS_SCOPE}}`
- **Critical Failure Points**:
  - `{{FAILURE_MODE_1}}`
  - `{{FAILURE_MODE_2}}`

---

## 7. 5-Point Enterprise Invariant Readiness Scorecard
- [ ] 1. Structural Envelope & Two-Plane Isolation (`<system_contract>`, `<untrusted_diff>`).
- [ ] 2. Absence of Nominal Cosplay Titles (zero roleplay fluff, explicit 7-tuple $\mathcal{I}$).
- [ ] 3. Epistemic Inversion & Negative Invariants Defined ($\mathcal{E}_{\text{adv}}$, $\ge 3$ negative constraints).
- [ ] 4. External Grammar Enforcement for Typed Outputs (`panel_verdict.schema.json`).
- [ ] 5. Severity-Over-Majority Veto Protocol Active (`adjudicate_panel.py`).
