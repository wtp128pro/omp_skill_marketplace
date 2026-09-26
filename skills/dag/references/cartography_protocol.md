# Cartography Protocol & Input Gap Analysis Specification

## 1. What is Cartography?

Cartography is the disciplined, exhaustive reconnaissance and structural mapping of the codebase, system topology, environment constraints, data contracts, and input surfaces before any planning or implementation occurs.

In the `dag` skill, **Cartography is a hard prerequisite**. Launching code generation, refactoring, or task planning without completed cartography is strictly prohibited.

---

## 2. The Five Pillars of Cartography

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 5 CARTOGRAPHY PILLARS                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Static Topology: Directory structure, module boundaries, entrypoints│
│ 2. Interface Contracts: APIs, data models, schema definitions, types   │
│ 3. System Invariants: Unbroken rules, concurrency models, invariants   │
│ 4. Input Gap Analysis (IGA): Auditing inputs against reputable sources │
│ 5. Failure & Edge Reconnaissance: Blast radius, error paths, limits   │
└────────────────────────────────────────────────────────────────────────┘
```

### Pillar 1: Static Topology Mapping
- Map the directory hierarchy, locating build configurations (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.).
- Identify project entry points, primary executables, and test harnesses.
- Chart dependency trees: internal module imports and third-party libraries.

### Pillar 2: Interface & Contract Cataloging
- Extract all public and internal interfaces, abstract base classes, and protocol definitions.
- Document input parameter types, return signatures, serialization formats (JSON, Protobuf, SQL schemas), and validation rules.
- Identify implicit contracts: ordering constraints, lifecycle hooks, and initialization requirements.

### Pillar 3: System Invariants
- Catalog the core invariants of the system (rules that must never be violated). Examples:
  - *"All database writes must execute within a transactional block."*
  - *"User IDs must be immutable and validated UUIDv4 strings."*
  - *"Thread-safe caches must never hold locks across asynchronous await boundaries."*

### Pillar 4: Input Gap Analysis (IGA) & Plausibility Trap Defense
An exhaustive examination of the user request and system requirements to detect any missing, contradictory, or underspecified inputs.

#### The Mechanistic Danger: The Plausibility Trap
When conditioned on an incomplete specification $X_{\text{obs}}$, unconstrained LLMs do not halt. Cross-entropy loss forces the model to sample median tutorial completions from pretraining:
$$P(Y \mid X_{\text{obs}}) = \int P(Y \mid X_{\text{obs}}, X_{\text{latent}}) P(X_{\text{latent}} \mid X_{\text{obs}}) dX_{\text{latent}}$$
The model generates clean-looking code that silently omits locks, transaction isolation, idempotency tokens, and timeout handlers.

#### The Three Formal Input Gap Classes:
1. **Class 1: Unstated Invariants & Boundary Preconditions (Sev-1 Blocking Veto)**
   - Database isolation level (`SERIALIZABLE`, `READ COMMITTED`), row-level locks (`SELECT ... FOR UPDATE`).
   - Numeric bounds ($x > 0, x \le \text{MAX\_INT}$), non-null invariants, collection empty states.
2. **Class 2: Contractual & Semantic Ambiguities (Sev-2 Major Veto)**
   - Return signatures, error payload schemas, character encodings (UTF-8), serialization formats.
3. **Class 3: Partial Failure Semantics & External Timeouts (Sev-1 Blocking Veto)**
   - Network timeout SLAs, retry storm defenses, distributed lock leases, unique idempotency fencing tokens.

#### Automated Verification Tool (`fdag iga-check`):
Before advancing to Phase 2 AWU decomposition, run the automated IGA auditor:
```bash
fdag iga-check --session-path .omp_wip/<session>/
# Or on raw specification text:
fdag iga-check --text "<user specification>"
```
*(Any Sev-1 gap triggers an immediate BLOCKING VETO, halting execution until invariants are declared).*

#### Reputable Sources Grounding:
- Every technical assertion, protocol specification, or external library behavior MUST be verified against authoritative primary documentation (official RFCs, IEEE/ISO standards, GitHub primary vendor repositories).
- All citations must be recorded in `00_cartography/input_gap_analysis.md`.

#### Strict Prohibition on Assumptions:
- NEVER fill in blanks or missing specifications with assumed defaults.
- If a requirement is missing:
  1. Search authoritative sources for canonical standards.
  2. Conduct internal structural analysis of system invariants.
  3. If unresolved and critical, halt and formulate a Socratic clarification for the human lead.
### Pillar 5: Failure Mode & Blast Radius Reconnaissance
- Catalog potential failure points: network timeouts, memory limits, race conditions, file locks.
- Map the "blast radius" (the extent of systems or components that could be affected if this work unit fails).

---

## 3. Ground Truth: Anti-Hallucination, Anti-Goldplating & Anti-Drift Guardrails

To ensure uncompromising engineering integrity, the agent must adhere to three negative axioms:

### Axiom A: Zero Hallucination
- Never invent libraries, methods, flags, parameters, or file paths that do not exist.
- Verify every symbol against the local filesystem or authoritative documentation before writing briefings or code.

### Axiom B: Zero Goldplating
- Deliver precisely what is specified in the task contract—nothing more, nothing less.
- Prohibit adding unrequested "future-proofing", gratuitous generic abstractions, unsolicited configuration toggles, or cosmetic refactorings.

### Axiom C: Zero Drift
- Maintain laser focus on the boundaries of each Atomic Work Unit (AWU).
- If an adjacent bug or improvement is discovered during implementation, DO NOT fix it within the active AWU. Instead, record it in the debriefing notes or propose it as a Bounded Graph Addition (BGA).

---

## 4. Grounding in Reputable Sources

When validating inputs, libraries, or protocols, only the following sources are recognized as reputable:

1. **First-Party Documentation**: Official documentation maintained by the language, framework, or vendor (e.g., Python Docs, MDN Web Docs, Go Docs, Rust Book, Microsoft Learn).
2. **Standardization Bodies**: IETF RFCs, W3C Recommendations, ISO/IEC standards, IEEE specifications.
3. **Primary Source Repositories**: Official release notes, GitHub source code, and issues maintained by primary authors.
4. **Authoritative Engineering Benchmarks**: Peer-reviewed engineering papers or official performance whitepapers.

*Prohibited sources*: Unverified personal blogs, speculative forum comments, or AI-generated summaries without primary citations.

---

## 5. Output Deliverables & File Locations

All cartography outputs must be written to disk in the session directory:

1. `.omp_wip/<session>/00_cartography/cartography_report.md`:
   - System topology diagram
   - Module matrix
   - Invariant catalog
   - Blast radius analysis
2. `.omp_wip/<session>/00_cartography/input_gap_analysis.md`:
   - Gap audit table
   - Reputable source citations
   - Resolution status for every ambiguity (Resolved via Spec / Non-Blocking Default / Blocking Escalation)
