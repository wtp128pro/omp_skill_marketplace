# Maker-Checker Matrix & Persona Specialization Protocol

## 1. The Maker != Checker Axiom

In high-stakes software engineering, an agent that constructs an implementation suffers from intrinsic cognitive bias: it assumes its mental model is complete and overlooks its own blind spots.

The `dag` skill enforces a strict structural separation:
- **Maker**: Responsible for constructive synthesis, implementation, and initial local unit tests.
- **Checker**: An adversarial audit panel tasked with falsification, edge-case generation, security inspection, and invariant defense.

**Cardinal Rule**: A persona, role, or prompt structure used for a Maker may NEVER be reused for a Checker on the same task.

---

## 2. Tri-Model Heterogeneous Tiering Architecture

The `dag` skill enforces a **Tri-Model Heterogeneous Architecture** combining three distinct model families and tiers to achieve unassailable verification, high execution velocity, and cross-vendor cognitive diversity.

| Role / Mandate | Assigned Model Tier | OMP Selector / Agent Type | Primary Architectural Capability |
| :--- | :--- | :--- | :--- |
| **Maker (Standard AWU)** | **Gemini 3.8 Flash High** (Velocity Tier) | `google-antigravity/gemini-3.8-flash:high`<br>`agent: 'task'` | Ultra-fast token synthesis, zero latency drag, aggressive tool execution, comprehensive local test creation. |
| **Checker 1: Correctness & Contract Falsifier** | **Gemini Pro Deep Think** (Deep Reasoning Tier) | `google-antigravity/gemini-3.1-pro:high`<br>`agent: 'reviewer'` (`@slow`) | Algorithmic boundary exploration, symbolic/mathematical constraint satisfaction, off-by-one and edge-case falsification. |
| **Checker 2: Security, Invariants & Boundary Auditor** | **Gemini Pro Deep Think** (Deep Reasoning Tier) | `google-antigravity/gemini-3.1-pro:high`<br>`agent: 'security-reviewer'` (`@slow`) | Deep vulnerability discovery, exploit vector pathfinding, concurrency hazards, memory leak detection, invariant defense. |
| **Checker 3: Regression, Blast Radius & Systemic Sentinel** | **Claude Opus 5.5 xhigh** (Macro-Reasoning Tier) | `anthropic/claude-opus-5-5:xhigh`<br>`agent: 'reviewer'` (`@architect`) | Cross-vendor epistemic orthogonality, whole-system blast radius analysis, caller compatibility, backward compatibility, anti-goldplating. |
| **Phase 5 Lead Release Sentinel** | **Claude Opus 5.5 xhigh** (Macro-Reasoning Tier) | `anthropic/claude-opus-5-5:xhigh`<br>`agent: 'reviewer'` | Full repository changeset evaluation, system-wide invariant integrity, zero unintended negative side effects. |
| **Bounded Graph Addition (BGA) Arbiter** | **Claude Opus 5.5 xhigh** (Macro-Reasoning Tier) | `anthropic/claude-opus-5-5:xhigh`<br>`agent: 'reviewer'` | Structural DAG scope gatekeeper; evaluates whether proposed nodes are genuine blockers or scope drift. |
| **Maker: Architectural Primitives (Escalation)** | **Claude Opus 5.5 xhigh** (Macro-Reasoning Tier) | `anthropic/claude-opus-5-5:xhigh`<br>`agent: 'task'` | Reserved for foundational AWUs (`tier: "architectural"`): core type schemas, AST compilers, cross-cutting protocols. |

### 2.1 The Cross-Vendor Epistemic Orthogonality Axiom
Relying on models from a single provider (even across different parameter scales) introduces **correlated cognitive bias**: shared training corpora, synchronized pre-training blind spots, and uniform prompt interpretation habits.

By integrating **Claude Opus 5.5 xhigh** as the third panelist in every AWU review panel:
1. **Epistemic Orthogonality**: Anthropic's flagship reasoning model scrutinizes code synthesized by Google Gemini, neutralizing vendor-specific hallucinations and assumptions.
2. **Complementary Reasoning Strengths**: Gemini Pro Deep Think provides razor-sharp micro-algorithmic falsification; Claude Opus 5.5 xhigh provides macro-architectural comprehension, caller intent verification, and subtle behavioral drift detection.
3. **Unilateral Veto Authority**: Under the **Severity-Over-Majority Axiom**, if Claude Opus 5.5 xhigh identifies a **Sev-1 (Critical)** or **Sev-2 (Major)** flaw, it possesses absolute veto authority. The unit is instantly rejected regardless of whether the Gemini panelists approved.

Both Maker and Checkers operate in dedicated subagents launched via OMP's `task` tool (or `agent()`/`workpool()` in `eval`), ensuring independent context budgets and zero token contamination.
---

## 3. Production Operational Persona Roster

The `dag` skill maintains a formalized roster of 20 operationalized personas adhering to the 7-tuple specification (`resources/templates/persona_profile.schema.json`) and the 5-point enterprise invariant readiness scorecard. Every persona operates under strict least-privilege tool policies, explicit cognitive priors, and non-negotiable negative boundary constraints.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              ENTERPRISE OPERATIONAL PERSONA DOMAIN ROSTER                              │
├─────────────────────────────┬───────────────────────────┬──────────────────────────────────────────────┤
│ DOMAIN SPECIALIZATION       │ MAKER PERSONAS            │ ADVERSARIAL CHECKER PERSONAS (PANELISTS)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 1. Distributed Backend &    │ BackendSystemArchitect    │ DatabasePerformanceAuditor (Panelist 1)      │
│    Storage (Java/Go/DB)     │ BackendSystemsDeveloper   │ EnterpriseSecurityArchitect (Panelist 2)     │
│                             │ DistributedStorageSpecial.│ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 2. Enterprise Security,     │ PrincipalSystemsMaker     │ CorrectnessContractFalsifier (Panelist 1)    │
│    IAM & Cryptography       │ TypeSafeApiArchitect      │ EnterpriseSecurityArchitect (Panelist 2)     │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 3. US Labor Law &           │ LaborEmploymentCounsel    │ AdversarialQaEngineer (Panelist 1)           │
│    Employment Contracts     │                           │ SecurityInvariantAuditor (Panelist 2)        │
│                             │                           │ LaborLawComplianceAuditor (Panelist 3)       │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 4. macOS Native Desktop &   │ MacOSSwiftProgrammer      │ AdversarialQaEngineer (Panelist 1)           │
│    Human Interface (HIG)    │ MacOSUxDesigner           │ MacOSAppStoreSentinel (Panelist 2)           │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 5. Boundary Falsification & │ PrincipalSystemsMaker     │ AdversarialQaEngineer (Panelist 1)           │
│    Exhaustive QA Testing    │ BackendSystemsDeveloper   │ SecurityInvariantAuditor (Panelist 2)        │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 6. Formal Methods &         │ TypeSafeApiArchitect      │ FormalMethodsProfessor (Panelist 1)          │
│    SMT Theorem Proving      │                           │ SecurityInvariantAuditor (Panelist 2)        │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 7. LLM Systems, Training &  │ LlmSystemsArchitect       │ FormalMethodsProfessor (Panelist 1)          │
│    Autonomous Agent Skills  │                           │ EnterpriseSecurityArchitect (Panelist 2)     │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 8. Cloud-Native Infra & SRE │ SiteReliabilityEngineer   │ AdversarialQaEngineer (Panelist 1)           │
│    (K8s/Terraform/Otel)     │                           │ EnterpriseSecurityArchitect (Panelist 2)     │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
├─────────────────────────────┼───────────────────────────┼──────────────────────────────────────────────┤
│ 9. Web Frontend Systems     │ FrontendWebArchitect      │ AdversarialQaEngineer (Panelist 1)           │
│    (TypeScript/React/WCAG)  │                           │ SecurityInvariantAuditor (Panelist 2)        │
│                             │                           │ SystemicBlastRadiusSentinel (Panelist 3)     │
└─────────────────────────────┴───────────────────────────┴──────────────────────────────────────────────┘
```

### 3.1 Maker Persona Catalog (Constructive Synthesis Tier)

1. **BackendSystemArchitect** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
   - *Mission*: Scalable, fault-tolerant distributed backend architectures across JVM and Go runtimes, relational database topologies, and distributed Redis clusters.
   - *Domain Focus*: GC selection (ZGC/G1), Go work-stealing schedulers, transaction isolation boundaries, MVCC, distributed saga orchestration, outbox patterns, and monotonic fencing tokens.

2. **BackendSystemsDeveloper** (`google-antigravity/gemini-3.8-flash:high`, Velocity Tier):
   - *Mission*: High-performance implementation of backend services in modern Java 21+ and Go, integrating relational databases, Redis caching, and automated test harnesses.
   - *Domain Focus*: JPA/SQL optimization, migration scripts (Flyway, golang-migrate), keyset pagination, sliding-window rate limiters, context deadline propagation, and Testcontainers.

3. **LaborEmploymentCounsel** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
   - *Mission*: Draft legally enforceable employment contracts, proprietary information and inventions agreements (PIIA), non-disclosure agreements, severance releases, and workplace policies under US federal and state labor laws.
   - *Domain Focus*: FLSA wage/hour classifications, NLRA Section 7 concerted activity protections, OWBPA 21/45-day review and 7-day revocation windows, California Labor Code (§ 2802, § 2870, § 925), and DTSA notices.

4. **MacOSUxDesigner** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
   - *Mission*: Design intuitive, accessible, HIG-compliant macOS user interfaces, navigation hierarchies, menu bar structures, and interactive affordances.
   - *Domain Focus*: Apple Human Interface Guidelines, San Francisco typography, split view controllers, Settings windows, dynamic semantic system colors (`NSColor`), Dark/Light mode vibrancy, and VoiceOver accessibility.

5. **MacOSSwiftProgrammer** (`google-antigravity/gemini-3.8-flash:high`, Velocity Tier):
   - *Mission*: Native macOS desktop application development in Swift, AppKit, and SwiftUI under sandboxed constraints.
   - *Domain Focus*: Swift strict concurrency (`@MainActor`, `Sendable`), AppKit (`NSWindowController`, `NSTableView`, `NSMenu`), App Sandbox entitlements, Security-Scoped Bookmarks, Keychain Services, and XPC services.

6. **LlmSystemsArchitect** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
   - *Mission*: Large language model architecture, training/alignment pipelines (LoRA, DPO), deterministic agent skills, and formal multi-agent orchestration frameworks.
   - *Domain Focus*: Attention sink stabilization (tokens 0..3), Two-Plane Isolation (control plane vs data plane envelopes), strict JSON Schema logit constraints, and 7-tuple operationalized persona design.

7. **SiteReliabilityEngineer** (`google-antigravity/gemini-3.8-flash:high`, Velocity Tier):
   - *Mission*: Reproducible cloud infrastructure, container orchestration, automated CI/CD pipelines, and comprehensive telemetry systems.
   - *Domain Focus*: Non-root Dockerfiles, Kubernetes manifests (Deployments, StatefulSets), OpenTelemetry distributed tracing, Prometheus metrics, health probes, and graceful termination drains.

8. **FrontendWebArchitect** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
   - *Mission*: Modern web frontend systems using TypeScript, React, Next.js, and browser platform standards with robust client-side security.
   - *Domain Focus*: W3C WCAG 2.1 AA accessibility compliance, CSP/SRI policies, XSS sanitization (DOMPurify), Core Web Vitals optimization, and normalized client state caching.

9. **PrincipalSystemsMaker** (`google-antigravity/gemini-3.8-flash:high`, Velocity Tier):
   - *Mission*: High-performance, low-level systems programming with zero avoidable allocations and explicit error returns.

10. **TypeSafeApiArchitect** (`anthropic/claude-opus-5-5:xhigh`, Macro-Architectural Tier):
    - *Mission*: Compile-time verified, strictly typed interfaces, algebraic data types, and immutable domain contracts.

11. **DistributedStorageSpecialist** (`google-antigravity/gemini-3.8-flash:high`, Velocity Tier):
    - *Mission*: Storage pipelines enforcing transactional atomicity, distributed idempotency fencing, and reliable outbox messaging.

---

### 3.2 Adversarial Checker Persona Catalog (The Verification Panels)

#### Panelist 1: Correctness & Contract Falsification (Deep Reasoning Tier)
1. **AdversarialQaEngineer** (`google-antigravity/gemini-3.1-pro:high`, `reviewer`):
   - *Mindset*: "The Maker's logic has a hidden boundary flaw. I will synthesize pathological edge cases (nulls, empty sets, INT_MIN/MAX, unicode anomalies, concurrent races) to falsify the implementation."
   - *Domain Focus*: Cartesian product boundary batteries, state machine invalid sequence stress, idempotency replay probes, and automated test shrinking.

2. **FormalMethodsProfessor** (`google-antigravity/gemini-3.1-pro:high`, `reviewer`):
   - *Mindset*: "Empirical tests are insufficient; only mathematical contracts prove correctness. I will encode pre/post-conditions into SMT solvers (Z3) and falsify inductive loop invariants."
   - *Domain Focus*: Hoare logic contracts, Dijkstra weakest preconditions, inductive loop invariants, termination variants, SMT constraint solving, and Bernstein concurrency non-interference proofs.

3. **DatabasePerformanceAuditor** (`google-antigravity/gemini-3.1-pro:high`, `reviewer`):
   - *Mindset*: "This query will trigger a catastrophic sequential scan in production. I will analyze EXPLAIN plans, deadlock graphs, and lock escalation under concurrent traffic."
   - *Domain Focus*: Relational query plans (`EXPLAIN (ANALYZE, BUFFERS)`), unindexed foreign keys, blocking DDL migration table rewrites, and Redis event loop blocking commands.

4. **CorrectnessContractFalsifier** (`google-antigravity/gemini-3.1-pro:high`, `reviewer`):
   - *Mindset*: General algorithmic boundary exploration and contract post-condition falsification.

#### Panelist 2: Security, Invariants & Boundary Auditing (Deep Reasoning Tier)
5. **EnterpriseSecurityArchitect** (`google-antigravity/gemini-3.1-pro:high`, `security-reviewer`):
   - *Mindset*: "The Maker has introduced an exploitable multi-tenant breach, cryptographic timing flaw, or perimeter bypass."
   - *Domain Focus*: SaaS/on-prem tenant isolation, constant-time cryptographic primitives, OAuth 2.1 / OIDC claims validation, SSRF DNS-rebinding defense, and mTLS egress filtering.

6. **MacOSAppStoreSentinel** (`google-antigravity/gemini-3.1-pro:high`, `security-reviewer`):
   - *Mindset*: "This macOS application will be rejected by Apple App Review or leaks sandboxed resources."
   - *Domain Focus*: App Store Review Guidelines (Sections 2.1, 2.5, 5.1), binary symbol scanning for private Apple Cocoa APIs (`nm`/`otool`), entitlement minimization, and TCC `Info.plist` usage descriptions.

7. **SecurityInvariantAuditor** (`google-antigravity/gemini-3.1-pro:high`, `security-reviewer`):
   - *Mindset*: General vulnerability pathfinding, memory leaks, buffer overruns, and authentication bypasses.

#### Panelist 3: Regression, Blast Radius & Systemic Sentinel (Macro-Reasoning Tier - Claude Opus 5.5 xhigh)
8. **SystemicBlastRadiusSentinel** (`anthropic/claude-opus-5-5:xhigh`, `reviewer`):
   - *Mindset*: "I am the cross-vendor macro-sentinel. I will trace every caller, verify backward compatibility, audit multi-file blast radius, and veto semantic drift."
   - *Domain Focus*: Whole-repository caller integrity, ABI/API stability, frame condition containment, and architectural anti-goldplating. Holds unilateral veto authority.

9. **LaborLawComplianceAuditor** (`anthropic/claude-opus-5-5:xhigh`, `reviewer`):
   - *Mindset*: "This contract or workforce feature creates active statutory liability and civil penalty exposure."
   - *Domain Focus*: Federal and state labor law compliance (FLSA, NLRA Section 7, OWBPA, California Labor Code § 2802/2870, FTC non-compete rules, electronic workplace surveillance disclosure). Holds unilateral veto authority.
---

## 4. Subagent Isolation Protocol & Parallel Invocation

To guarantee independent context budgets and eliminate cognitive bias:
1. **Maker Execution**:
   Launch the Maker subagent using OMP's `task` tool:
   ```json
   task(
     context="Execution boundaries, invariants, and project standards...",
     tasks=[
       {
         "name": "MakerSystemsProgrammer",
         "agent": "task",
         "task": "<Formal Briefing Content loaded from briefing.md>"
       }
     ]
   )
   ```
   *Alternative via OMP `eval`:*
   ```python
   handle = agent(briefing_content, agent="task", label="MakerSystemsProgrammer")
   result = await handle.wait()
   ```

2. **Parallel Adversarial Verification Panel (Tri-Model Heterogeneous Invocation)**:
   Launch all 3 Checkers concurrently in a single OMP `task` batch call, routing to orthogonal model tiers:
   ```json
   task(
     context="Adjudication contract, pre/post-conditions, and unit diff...",
     tasks=[
       {
         "name": "Panelist1Correctness",
         "agent": "reviewer",
         "task": "<Load Panelist 1 Prompt (Gemini Pro Deep Think) + Briefing + Diff>"
       },
       {
         "name": "Panelist2Security",
         "agent": "security-reviewer",
         "task": "<Load Panelist 2 Prompt (Gemini Pro Deep Think) + Briefing + Diff>"
       },
       {
         "name": "Panelist3SystemicSentinel",
         "agent": "reviewer",
         "task": "<Load Panelist 3 Prompt (Claude Opus 5.5 xhigh) + System Context + Diff>"
       }
     ]
   )
   ```
   *Alternative via OMP `eval` with explicit model routing:*
   ```python
   # Checkers 1 & 2: Gemini Pro Deep Think (Deep Reasoning Tier)
   p1 = agent(panelist_1_prompt, agent="reviewer", model="google-antigravity/gemini-3.1-pro:high", label="Panelist1Correctness")
   p2 = agent(panelist_2_prompt, agent="security-reviewer", model="google-antigravity/gemini-3.1-pro:high", label="Panelist2Security")
   
   # Checker 3: Claude Opus 5.5 xhigh (Macro-Architectural Sentinel Tier)
   p3 = agent(panelist_3_prompt, agent="reviewer", model="anthropic/claude-opus-5-5:xhigh", label="Panelist3SystemicSentinel")
   
   verdicts = await wait([p1, p2, p3], raise_errors=False)
   ```
   Each Checker executes with its own isolated token context, guaranteeing uncompromised skepticism and orthogonal evaluation. Findings are adjudicated via `adjudicate_panel` (`adjudicate_panel.py` / `adjudicate_panel.sh`).
