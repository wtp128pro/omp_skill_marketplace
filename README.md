# OMP Skill Marketplace

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](requirements.txt)
[![OMP: Compatible](https://img.shields.io/badge/OMP-v18%2B-orange.svg)](https://omp.sh)
[![Formal Methods: Z3 & Hypothesis](https://img.shields.io/badge/Formal%20Methods-Z3%20%7C%20Hypothesis-purple.svg)](skills/dag/scripts/smt_contract_verifier.py)
[![Author: wtp128pro](https://img.shields.io/badge/Published%20By-wtp128pro-darkblue.svg)](https://github.com/wtp128pro)

Curated marketplace of production-grade, battle-tested skills for the **OMP (One More Prompt / Open Multi-Agent Platform)** autonomous agent ecosystem.

---

## ⚠️ Important Legal Notices & Safety Warning

> **DISCLAIMER**: All software, skills, scripts, prompts, and personas in this repository are provided **"AS IS"** without warranty of any kind. Autonomous multi-agent workflows execute arbitrary shell commands, manipulate files, and make upstream API calls. Use at your own risk. 
> 
> Outputs produced by simulated personas (such as `LaborEmploymentCounsel`, `EnterpriseSecurityArchitect`, or `FormalMethodsProfessor`) are synthetically generated text and **DO NOT** constitute certified legal, financial, security, or professional architectural advice. Users are solely responsible for monitoring all third-party LLM API token consumption, fees, and system actions. 
>
> **Read the complete binding [DISCLAIMER.md](DISCLAIMER.md) before installing or executing any skill.**

---

## Available Skills

| Skill | Moniker | Description | Primary Engine |
| :--- | :--- | :--- | :--- |
| **[Formal-Agentic DAG Engine](skills/dag/SKILL.md)** | `dag` | Distributed engineering director for executing complex software initiatives via Directed Acyclic Graphs, strict Maker!=Checker orthogonality, 3-agent adversarial verification panels, severity-over-majority vetoes, SMT/property-based contract falsification, and bounded self-learning loops. | Python 3 + Z3 + Hypothesis + OMP Subagents |

---

## Skill Spotlight: `dag` (Formal-Agentic DAG Engine)

The `dag` skill transforms an AI agent from a linear, single-threaded executor into an enterprise-grade distributed engineering director. Every complex objective is mapped, decomposed into a mathematically validated Directed Acyclic Graph, isolated into subagents with independent context budgets, and scrutinized by adversarial verification panels.

### Non-Negotiable Operational Axioms
1. **Cartography Before Construction**: Comprehensive mapping of directory trees, call graphs, schemas, and input gaps before writing any code.
2. **Zero Assumptions & Input Gap Primacy**: Missing specifications are validated against authoritative primary sources (RFCs, IEEE/ISO standards) or flagged as blocking gaps—never guessed.
3. **Maker != Checker Orthogonality**: The subagent that authors code (`Maker`) is structurally prohibited from verifying it (`Checker`). Different roles, models, and isolated context windows are enforced.
4. **Tri-Model Heterogeneous Tiering**:
   - **Tier 1 (Synthesis / Maker)**: High-throughput execution powered by **Gemini 3.8 Flash High** (`agent: 'task'`).
   - **Tier 2 (Deep Reasoning Checkers)**: Algorithmic & security falsification powered by **Gemini Pro Deep Think** (`agent: 'reviewer'`, `agent: 'security-reviewer'`).
   - **Tier 3 (Macro-Reasoning & Architectural Sentinel)**: Systemic blast radius and invariant review powered by **Claude Opus 5.5 xhigh** with unilateral veto authority.
5. **Mandatory 3-Agent Adversarial Verification**: Every work unit is evaluated concurrently by 3 distinct checkers (Contract Falsifier, Security Auditor, Systemic Blast Radius Sentinel).
6. **Severity Over Majority Veto**: A single **Sev-1 (Critical)** or **Sev-2 (Major)** flaw unconditionally vetoes approval—problem magnitude overrides vote counts.
7. **Active Bounded Self-Learning ($N \le 3$)**: Panel rejections automatically extract failure counterexamples and negative constraints into `learnings.jsonl` and re-brief the Maker up to 3 iterations before human escalation.
8. **Bernstein Concurrency Non-Interference**: Parallel execution of independent peer units is mathematically verified ($\mathcal{R}_u \cap \mathcal{W}_v = \emptyset \land \mathcal{W}_u \cap \mathcal{R}_v = \emptyset \land \mathcal{W}_u \cap \mathcal{W}_v = \emptyset$).
9. **Frame Containment & Mathematical Modifies Sets**: Units declare strict Write-Sets (`frame_conditions.modifies`). Unauthorized mutations trigger an immediate Sev-1 Frame Breach Veto.
10. **SMT & Property-Based Falsification**: Automated contract verification using Z3 symbolic solving, Hypothesis property shrinking, and native boundary exploration.
11. **Phase 1.5 Layered Socratic Input Clarification**: Prior to DAG decomposition and strictly post-Cartography, inputs are audited across 3 layers (Structural, Invariant, Socratic). Any ambiguity is resolved via single-question Socratic dialogue in plain language with evaluated options and `(Recommended)` first.
12. **Execution-Phase Assumption Invalidation Human Gate**: Any empirical discovery during execution invalidating a prior assumption immediately halts the unit (`status: BLOCKED`) and enforces an unappealable Human Gate.

### Specialized Persona Catalog
The skill includes 20+ specialized expert personas in `skills/dag/resources/personas/`:
- `PrincipalSystemsMaker`: Core implementation architect
- `CorrectnessContractFalsifier`: Formal invariant & edge-case checker
- `SecurityInvariantAuditor`: Concurrency race & vulnerability auditor
- `SystemicBlastRadiusSentinel`: Whole-system backwards-compatibility sentinel
- `EnterpriseSecurityArchitect`: Multi-tenant security & crypto auditor
- `FormalMethodsProfessor`: Mathematical pre/post-condition validator
- `LaborEmploymentCounsel`: Workplace & statutory policy compliance auditor
- `DatabasePerformanceAuditor`: Query plan, locking, and migration specialist

---

## Installation in OMP

You can install skills from this marketplace into OMP using any of the following methods:

### Method 1: Global OMP Skill Directory via Git Clone / Symlink (Recommended)

Cloning the repository and linking the skill directly into your global `~/.omp/agent/skills/` directory provides instant access across all OMP projects:

```bash
# 1. Clone the marketplace repository to your preferred location
git clone https://github.com/wtp128pro/omp_skill_marketplace.git ~/Developer/omp_skill_marketplace

# 2. Ensure your global OMP skills directory exists
mkdir -p ~/.omp/agent/skills

# 3. Create a symbolic link to the skill (recommended for automatic git updates):
ln -sf ~/Developer/omp_skill_marketplace/skills/dag ~/.omp/agent/skills/dag

# Alternatively, copy the skill directory if you do not want a symlink:
# cp -R ~/Developer/omp_skill_marketplace/skills/dag ~/.omp/agent/skills/dag
```

Verify that OMP detects the skill by running:
```bash
omp "Check available skills"
# or inspect ~/.omp/agent/skills/dag/SKILL.md
```

### Method 2: Project-Local Workspace Installation

If you prefer to bundle the skill strictly within a specific repository or project workspace:

```bash
cd /path/to/your/project

# Create local .omp skills directory
mkdir -p .omp/skills

# Copy or symlink the dag skill
cp -R ~/Developer/omp_skill_marketplace/skills/dag .omp/skills/dag
# or: ln -sf ~/Developer/omp_skill_marketplace/skills/dag .omp/skills/dag
```

### Method 3: Via OMP Skillshare CLI (`omp skill`)

If installing from the published Skillshare package registry:

```bash
# Install globally
omp skill install -g @wtp128pro/dag

# Or install locally for the current project
omp skill install @wtp128pro/dag
```

### Step 4: Configure Model Roles & Subagent Overrides (`~/.omp/agent/config.yml`)

**Crucial Prerequisite**: The `dag` engine relies on OMP's multi-tiered role system (`default`, `slow`, `architect`, `smol`) and subagent overrides to orchestrate heterogeneous panels. Without this configuration, OMP subagents (`reviewer`, `security-reviewer`, `task`) cannot resolve their respective reasoning tiers and will collapse into a single default model family.

Create or update your global OMP configuration file at `~/.omp/agent/config.yml`:

```yaml
setupVersion: 2
modelRoles:
  default: google-antigravity/gemini-3.8-flash:high
  slow: google-antigravity/gemini-3.1-pro:high
  architect: anthropic/claude-opus-5-5:xhigh
  smol: anthropic/claude-haiku-4-5

task:
  agentModelOverrides:
    reviewer: anthropic/claude-opus-5-5:xhigh
    security-reviewer: google-antigravity/gemini-3.1-pro:high
```

Or configure it directly from your terminal using the OMP CLI:
```bash
omp config set task.agentModelOverrides '{"reviewer": "anthropic/claude-opus-5-5:xhigh", "security-reviewer": "google-antigravity/gemini-3.1-pro:high"}'
```

> **CRITICAL: Subagent Model Overrides (`task.agentModelOverrides`)**:
> By default, OMP subagents spawned via the `task` tool inherit the active session's default model unless mapped in `task.agentModelOverrides`.
> - `reviewer`: Bound to **Claude Opus 5.5 xhigh** (`@architect`) for whole-system blast radius, backward compatibility, and unilateral veto authority.
> - `security-reviewer`: Bound to **Gemini Pro Deep Think** (`@slow`) for deep algorithmic boundary exploration and security invariant falsification.
> - `task`: Handled by **Gemini 3.8 Flash High** (`default`) for rapid code synthesis and tool orchestration.
---

## Updating Skills in OMP

### When Installed via Git Clone or Symlink
Simply pull the latest changes from the marketplace repository:
```bash
cd ~/Developer/omp_skill_marketplace
git pull origin main

# If you copied files instead of using a symlink:
cp -R skills/dag/* ~/.omp/agent/skills/dag/
```

### When Installed via OMP CLI
```bash
# Update globally
omp skill update -g @wtp128pro/dag

# Or update local workspace
omp skill update @wtp128pro/dag
```

---

## Required Software Packages & System Prerequisites

### 1. System Requirements
- **Operating System**: macOS (Darwin arm64/x86_64), Linux (x86_64/aarch64), or Windows WSL2.
- **Shell**: `bash` (v4.0+ recommended) or POSIX-compliant shell.
- **Version Control**: `git` (v2.30+).
- **OMP**: v18.0.0 or later (`brew install omp` or official installer).

### 2. Python Runtime & Dependencies
- **Python**: Version **3.10** or newer (tested on Python 3.10, 3.11, 3.12, 3.13, and 3.14).
- **Core Python Packages**:
  Install required dependencies via `pip`:

  ```bash
  pip install -r requirements.txt
  ```

  Or install individually:
  ```bash
  pip install "jsonschema>=4.20.0" "hypothesis>=6.90.0" "z3-solver>=4.12.0"
  ```

#### Dependency Breakdown:
| Package | Version Requirement | Purpose in F-DAG Engine |
| :--- | :--- | :--- |
| `jsonschema` | `>=4.20.0` | Validates `dag_manifest.json`, `panel_verdicts.json`, and persona specifications against JSON schemas. |
| `z3-solver` | `>=4.12.0` | High-performance Microsoft Z3 SMT solver used by Panelist 1 for symbolic bitvector, arithmetic, and Hoare-logic post-condition falsification. |
| `hypothesis` | `>=6.90.0` | Property-based testing and stateful test-case shrinking used to find minimal counterexamples violating pre/post-conditions. |

*Note: If `z3-solver` or `hypothesis` is not installed, `smt_contract_verifier.py` automatically falls back to native boundary testing, but full formal falsification requires all packages.*

---

## Required LLMs & Model Configuration

The `dag` skill enforces a **Tri-Model Heterogeneous Tiering Architecture** to eliminate vendor cognitive monoculture and prevent shared model-family blind spots.

### Model Tier Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Tri-Model Heterogeneous Tiering                       │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 1: Synthesis / Maker Subagents                                   │
│  Model: Gemini 3.8 Flash High (google-antigravity/gemini-3.8-flash:high)│
│  Agent: 'task'                                                         │
│  Function: High-throughput code implementation and file edits          │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 2: Deep Reasoning Algorithmic & Security Checkers                │
│  Model: Gemini Pro Deep Think (google-antigravity/gemini-3.1-pro:high) │
│  Agents: 'reviewer', 'security-reviewer'                               │
│  Function: SMT falsification, boundary exploits, concurrency analysis  │
├────────────────────────────────────────────────────────────────────────┤
│  Tier 3: Macro-Reasoning & Architectural Sentinel                      │
│  Model: Claude Opus 5.5 xhigh (anthropic/claude-opus-5-5:xhigh)         │
│  Agent: 'reviewer' (Cross-vendor auditor with UNILATERAL VETO)        │
│  Function: Multi-file blast radius, backwards compatibility, BGA       │
└────────────────────────────────────────────────────────────────────────┘
```

### Supported Model Alternatives
If the primary models are unavailable in your environment, the following models can be substituted:
- **Tier 1 (Maker)**: `google-antigravity/gemini-3.8-flash:high`, `google/gemini-2.5-flash`, `anthropic/claude-3-7-sonnet`, `openai/gpt-4o`
- **Tier 2 (Deep Reasoning Checkers)**: `google-antigravity/gemini-3.1-pro:high`, `google-antigravity/gemini-3-pro:high`, `openai/o1`, `openai/o3-mini:high`, `anthropic/claude-3-7-sonnet:thinking`
- **Tier 3 (Macro-Reasoning Sentinel)**: `anthropic/claude-opus-5-5:xhigh`, `anthropic/claude-3-opus`, `openai/gpt-4.5-preview`

### Recommended OMP Configuration (`~/.omp/agent/config.yml`)
To configure your model roles for optimal DAG orchestration:

```yaml
setupVersion: 2
modelRoles:
  default: google-antigravity/gemini-3.8-flash:high
  slow: google-antigravity/gemini-3.1-pro:high
  architect: anthropic/claude-opus-5-5:xhigh
  smol: anthropic/claude-haiku-4-5

task:
  agentModelOverrides:
    reviewer: anthropic/claude-opus-5-5:xhigh
    security-reviewer: google-antigravity/gemini-3.1-pro:high
```

### Provider Authentication: OMP `/login` & API Keys

You can authenticate the required model providers either via OMP's native provider login (recommended) or via standard environment variables.

#### Option 1: Native OMP Provider Login via `/login` (Recommended)

Authenticate your accounts directly inside an interactive `omp` session using the `/login` slash command, or from your terminal using `omp login`:

1. **Google Antigravity / Gemini (Tiers 1 & 2)**:
   ```bash
   # Terminal command:
   omp login antigravity
   
   # Or inside an active omp session:
   /login antigravity
   ```

2. **Anthropic Claude (Tier 3 Macro-Reasoning Sentinel)**:
   ```bash
   omp login anthropic
   
   # Or inside an active omp session:
   /login anthropic
   ```

3. **OpenAI (Optional / Alternative reasoning models)**:
   ```bash
   # Terminal command:
   omp login openai-codex
   
   # Or inside an active omp session:
   /login openai-codex
   ```

#### Option 2: Environment Variables (Headless / CI Automation)

Alternatively, set the appropriate API keys in your environment (e.g., in `~/.bashrc`, `~/.zshrc`, or `.env`):

```bash
# Google Gemini (Tiers 1 & 2)
export GEMINI_API_KEY="your-gemini-api-key"

# Anthropic Claude (Tier 3 Sentinel & Architectural Escalations)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# OpenAI (Optional / Alternative reasoning models)
export OPENAI_API_KEY="your-openai-api-key"
```

---

## Toolchain & Verification CLI (`fdag`)

The `dag` skill includes a unified CLI toolchain (`fdag.py` and shell wrapper `fdag.sh`) located in `skills/dag/scripts/`:

```bash
# Show all available commands
python3 skills/dag/scripts/fdag.py --help
# Or using the shell wrapper:
./skills/dag/scripts/fdag.sh --help
```

### CLI Subcommands Overview:
- `fdag init --task-moniker <name>`: Scaffold `.omp_wip/` timestamped workspace.
- `fdag validate --manifest-path <path>`: Validate DAG acyclicity, schema, depth, and Bernstein concurrency non-interference.
- `fdag scaffold --unit-id <AWU-ID>`: Instantiate all 5 mandatory contracts for an Atomic Work Unit (`briefing.md`, `briefing.json`, `panel_verdicts.json`, `learnings.jsonl`, `debriefing.md`).
- `fdag falsify`: Run multi-engine contract verification (Z3 SMT solver, Hypothesis property fuzzing, native boundary exploration).
- `fdag frame-check --unit-id <AWU-ID>`: Audit git diff against declared `frame_conditions.modifies` to prevent unauthorized file mutations.
- `fdag adjudicate --unit-id <AWU-ID>`: Enforce Severity-Over-Majority rule on 3-agent panel verdicts.
- `fdag scorecard --persona-path <path>`: Evaluate 5-Point Enterprise Invariant Readiness Scorecard on prompt files.
- `fdag iga-check --input-file <path>`: Detect 3-Class Input Gaps to prevent the LLM Plausibility Trap.
- `fdag clarify --session-path <path>`: Execute Phase 1.5 Layered Socratic Input Clarification Gate (supports `--step` and `--resolve`).
- `fdag invalidate-assumption --unit-id <ID>`: Register dynamic discovery assumption invalidation and trigger mandatory Human Gate.
- `fdag resolve-invalidation --invalidation-id <ID>`: Formally resolve Human Gate and unblock AWU.
- `fdag test`: Execute the comprehensive test suite (`test_fdag_suite.py`).

### Running the Test Suite
To verify the entire toolchain and environment:
```bash
python3 skills/dag/scripts/test_fdag_suite.py
```

Expected output:
```text
Ran 19 tests in 0.107s
OK
```

---

## Repository Structure

```text
omp_skill_marketplace/
├── LICENSE                            # MIT License (Copyright 2026 wtp128pro)
├── DISCLAIMER.md                      # Comprehensive Legal Disclaimers & Terms of Use
├── README.md                          # Marketplace guide, installation, and documentation
├── requirements.txt                   # Python package dependencies
├── dag -> skills/dag                  # Convenience symlink to default dag skill
└── skills/
    └── dag/                           # Formal-Agentic DAG Engine skill package
        ├── SKILL.md                   # Main OMP skill instruction manifesto
        ├── requirements.txt           # Skill-specific package dependencies
        ├── DISCLAIMER.md -> ../../DISCLAIMER.md
        ├── examples/
        │   └── sample_walkthrough.md  # End-to-end execution example
        ├── references/                # In-depth architectural & mathematical specifications
        │   ├── adversarial_panel.md
        │   ├── bounded_verification.md
        │   ├── briefing_debriefing_spec.md
        │   ├── cartography_protocol.md
        │   ├── code_quality_standard.md
        │   ├── communication_standards.md
        │   ├── dag_graph_protocol.md
        │   ├── fdag_architecture_blueprint.md
        │   ├── formal_methods_protocol.md
        │   ├── maker_checker_matrix.md
        │   └── operationalized_personas_spec.md
        ├── resources/
        │   ├── personas/              # 20+ specialized 7-tuple agent personas (JSON)
        │   └── templates/             # JSON schemas and markdown contract templates
        └── scripts/                   # Production CLI toolchain and validation scripts
            ├── fdag.py / fdag.sh
            ├── validate_dag.py / validate_dag.sh
            ├── init_dag_session.py / init_dag_session.sh
            ├── scaffold_dag_unit.py / scaffold_dag_unit.sh
            ├── adjudicate_panel.py / adjudicate_panel.sh
            ├── frame_condition_auditor.py
            ├── input_gap_auditor.py
            ├── audit_readiness_scorecard.py
            ├── smt_contract_verifier.py
            └── test_fdag_suite.py
```

---

## Contributing

Contributions, bug reports, and new skill submissions are welcome. Please ensure that all submissions:
1. Include exhaustive tests adhering to `skills/dag/scripts/test_fdag_suite.py`.
2. Do not introduce breaking contract changes or unvalidated dependencies.
3. Adhere to the strict Maker!=Checker and formal verification principles.
4. Maintain full compliance with [DISCLAIMER.md](DISCLAIMER.md).

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2026 **wtp128pro**.
