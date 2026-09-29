#!/usr/bin/env python3
"""
init_dag_session.py - Initialize a new DAG orchestration session in the .omp_wip directory.

Creates:
.omp_wip/<yyyy-MM-dd>_<HH-mm-ss>_<TaskMoniker>/
├── 00_cartography/
│   ├── cartography_report.md
│   └── input_gap_analysis.md
├── 01_dag/
│   ├── dag_manifest.json
│   ├── dag_graph.md
│   └── bga_proposals/
├── units/
└── 99_final_review/
    ├── adversarial_regression_audit.md
    └── session_debrief.md
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path


def sanitize_moniker(moniker: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "-", moniker).lower().strip("-_")
    return cleaned if cleaned else "dag-task"


def find_workspace_root(start_dir: Path) -> Path:
    curr = start_dir.resolve()
    home_dir = Path.home().resolve()
    for parent in [curr] + list(curr.parents):
        if parent == home_dir:
            if (parent / ".omp_wip").exists() and curr == home_dir:
                return parent
            continue
        if (parent / ".git").exists() or (parent / ".omp_wip").exists() or (parent / ".omp").exists():
            return parent
    return curr


def init_dag_session(
    task_moniker: str = "dag-task",
    workspace_root: str = None,
    json_output: bool = False,
    task_description: str = "",
    spec_file: str = ""
):
    if spec_file:
        sf_path = Path(spec_file).resolve()
        if sf_path.exists():
            try:
                task_description = sf_path.read_text(encoding="utf-8").strip()
            except Exception as e:
                print(f"[WARN] Failed to read spec file {sf_path}: {e}", file=sys.stderr)
        else:
            print(f"[WARN] Specified spec file does not exist: {sf_path}", file=sys.stderr)

    if workspace_root:
        ws_path = Path(workspace_root).resolve()
        if not ws_path.exists():
            print(f"[ERROR] Specified workspace root does not exist: {ws_path}", file=sys.stderr)
            sys.exit(1)
    else:
        ws_path = find_workspace_root(Path.cwd())
    safe_moniker = sanitize_moniker(task_moniker)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    iso_now = now.isoformat()
    session_dirname = f"{timestamp}_{safe_moniker}"

    wip_root = ws_path / ".omp_wip"
    session_path = wip_root / session_dirname

    subdirs = [
        "00_cartography",
        "01_dag",
        "01_dag/bga_proposals",
        "units",
        "99_final_review",
    ]
    for sub in subdirs:
        (session_path / sub).mkdir(parents=True, exist_ok=True)

    # 1. Base DAG Manifest Skeleton
    dag_dir = session_path / "01_dag"
    cartography_dir = session_path / "00_cartography"
    manifest_path = dag_dir / "dag_manifest.json"
    manifest_skeleton = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "session_id": session_dirname,
        "task_moniker": safe_moniker,
        "task_description": task_description or "",
        "graph_version": 2,
        "created_at": iso_now,
        "input_clarification": {
            "status": "PENDING",
            "total_questions": 0,
            "resolved_questions": 0,
            "dialogues_file": "00_cartography/socratic_dialogues.json"
        },
        "invalidated_assumptions": [],
        "nodes": [],
    }
    manifest_path.write_text(json.dumps(manifest_skeleton, indent=2), encoding="utf-8")
    # 2. DAG Graph Mermaid Skeleton
    dag_graph_path = session_path / "01_dag" / "dag_graph.md"
    dag_graph_skeleton = f"""# DAG Execution Graph: {safe_moniker}

```mermaid
flowchart TD
    %% Define nodes and dependencies here
```

### Execution Strategy & Topological Sequence
*(To be populated during Phase 2)*
"""
    dag_graph_path.write_text(dag_graph_skeleton, encoding="utf-8")

    # 3. Cartography Report Skeleton
    cartography_path = session_path / "00_cartography" / "cartography_report.md"
    task_desc_section = f"\n- **Task Objective & User Specification**: {task_description}" if task_description else "\n- **Task Objective & User Specification**: *(To be populated from user prompt)*"
    cartography_skeleton = f"""# Cartography & System Architecture Report

## 1. Executive Summary
- **Session Moniker**: {safe_moniker}
- **Generated At**: {iso_now}
- **Session Directory**: {session_path}{task_desc_section}

## 2. Static Codebase Topology
- **Root Directory**: {ws_path}
- **Status**: Reconnaissance In Progress

## 3. Core Interface & Schema Catalog
*(To be populated during Phase 1)*

## 4. Invariant Catalog (Non-Negotiable System Rules)
*(To be populated during Phase 1)*

## 5. Blast Radius & Failure Mode Analysis
*(To be populated during Phase 1)*
"""
    cartography_path.write_text(cartography_skeleton, encoding="utf-8")

    # 3.5 Task Specification (Phase 1 / 1.5 input audit ground truth)
    task_spec_path = session_path / "00_cartography" / "task_specification.md"
    if task_description:
        task_spec_content = f"""# Task Specification & User Requirements

## 1. Original User Request
{task_description}

## 2. Stated Scope & Invariants
*(Cross-referenced against codebase topology and input gap analysis)*
"""
    else:
        task_spec_content = """# Task Specification & User Requirements

## 1. Original User Request
*(Pending user task description. Provide via --task-description or edit this file)*

## 2. Stated Scope & Invariants
*(To be populated during Phase 1 Cartography)*
"""
    task_spec_path.write_text(task_spec_content, encoding="utf-8")
    # 4. Input Gap Analysis Skeleton
    iga_path = session_path / "00_cartography" / "input_gap_analysis.md"
    iga_scope_section = f"## 0. User Specification & Scope\n{task_description}\n\n" if task_description else ""
    iga_skeleton = f"""# Input Gap Analysis (IGA) & Reputable Source Citations

{iga_scope_section}## 1. Input Parameter & Contract Audit
| Parameter / Requirement | Status | Reputable Source Citation | Resolution Rationale |
| :--- | :--- | :--- | :--- |

## 2. Unverified Gaps & Blocking Inquiries
*(Document any missing requirements; prohibit arbitrary assumptions)*
"""
    iga_path.write_text(iga_skeleton, encoding="utf-8")
    # 4.5 Socratic Dialogues Ledger Skeleton (Phase 1.5)
    socratic_path = cartography_dir / "socratic_dialogues.json"
    socratic_skeleton = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "session_id": session_dirname,
        "dialogue_phase": "phase_1_5_input_clarification",
        "total_questions": 0,
        "resolved_questions": 0,
        "status": "PENDING",
        "dialogues": []
    }
    socratic_path.write_text(json.dumps(socratic_skeleton, indent=2), encoding="utf-8")

    # 5. Final Side-Effect Regression Audit Skeleton
    regression_path = session_path / "99_final_review" / "adversarial_regression_audit.md"
    regression_skeleton = f"""# Phase 5: Global 3-Agent Adversarial Regression & Side-Effect Panel

**Target Session**: {session_dirname}  
**Audit Timestamp**: Pending Execution  

## Panelist A: System Blast Radius Auditor (Claude Opus 5.5 xhigh)
- **Status**: Pending
- **Findings**: *(Audit untouched systems, interfaces, and regression suites)*

## Panelist B: Performance & Concurrency Inquisitor (Gemini Pro Deep Think)
- **Status**: Pending
- **Findings**: *(Audit resource leaks, latency regressions, thread-safety)*

## Panelist C: Architectural Integrity Sentinel (Claude Opus 5.5 xhigh)
- **Status**: Pending
- **Findings**: *(Audit naming conventions, modular purity, type safety)*
## Adjudicated Outcome
- **Highest Defect Severity**: None
- **Final Regression Signoff**: Pending
"""
    regression_path.write_text(regression_skeleton, encoding="utf-8")

    # 6. Final Session Debrief Skeleton
    session_debrief_path = session_path / "99_final_review" / "session_debrief.md"
    session_debrief_skeleton = f"""# Phase 6: Session Debrief & Handover Summary

- **Task Moniker**: {safe_moniker}
- **Session ID**: {session_dirname}
- **Completed At**: Pending

## 1. Objective Delivery
*(Summary of completed functional milestones)*

## 2. Global Deliverables Registry
*(Comprehensive list of created or modified source files)*

## 3. Verification & Invariant Proofs
*(Summary of unit tests, adversarial panels, and regression audits)*

## 4. Adversarial Regression Panel Findings
*(Summary of Phase 5 3-agent adversarial regression audit findings)*

## 5. Architectural Invariants Preserved
*(Explicit validation that all cartography system invariants remain intact)*

## 6. Socratic Handover & Operational Notes
*(Human-facing plain-language summary with all technical terms explained inline)*
"""
    session_debrief_path.write_text(session_debrief_skeleton, encoding="utf-8")

    # Emit subagent routing specification to guarantee tri-model architecture
    routing_spec = {
        "maker_tier": {
            "agent": "task",
            "recommended_role": "default",
            "model": "google-antigravity/gemini-3.8-flash:high"
        },
        "checker_tiers": {
            "Panelist1_Correctness": {"agent": "reviewer", "role": "slow", "model": "google-antigravity/gemini-3.1-pro:high"},
            "Panelist2_Security": {"agent": "security-reviewer", "role": "slow", "model": "google-antigravity/gemini-3.1-pro:high"},
            "Panelist3_SystemicSentinel": {"agent": "reviewer", "role": "architect", "model": "anthropic/claude-opus-5-5:xhigh"}
        },
        "omp_cfg_recommendation": {
            "task.agentModelOverrides": {
                "reviewer": "anthropic/claude-opus-5-5:xhigh",
                "security-reviewer": "google-antigravity/gemini-3.1-pro:high"
            }
        }
    }
    (dag_dir / "subagent_routing_matrix.json").write_text(json.dumps(routing_spec, indent=2), encoding="utf-8")

    result = {
        "SessionPath": str(session_path),
        "SessionDirName": session_dirname,
        "ManifestPath": str(manifest_path),
        "CartographyPath": str(cartography_path),
        "TaskSpecificationPath": str(task_spec_path),
        "IgaPath": str(iga_path),
        "SocraticDialoguesPath": str(socratic_path),
        "DagGraphPath": str(dag_graph_path),
        "SubagentRoutingMatrixPath": str(dag_dir / "subagent_routing_matrix.json"),
        "RegressionAuditPath": str(regression_path),
        "SessionDebriefPath": str(session_debrief_path)
    }
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"\033[36m==> Initializing DAG Session in: {session_path}\033[0m")
        print(f"\033[32m==> DAG Session successfully initialized.\033[0m")
        print(f"Session Directory: {session_path}")
        print(f"Manifest Path:     {manifest_path}")
        print(f"Cartography Path:  {cartography_path}")
        if task_description:
            print(f"Task Spec Path:    {task_spec_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Initialize a new DAG orchestration session in .omp_wip.")
    parser.add_argument("-t", "--task-moniker", default="dag-task", help="Short task moniker / slug")
    parser.add_argument("-d", "--task-description", "--task-desc", "--spec-text", default="", help="Verbatim user request or task specification")
    parser.add_argument("-s", "--spec-file", default="", help="Path to raw specification text file")
    parser.add_argument("-w", "--workspace-root", default="", help="Workspace root directory")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    init_dag_session(
        task_moniker=args.task_moniker,
        workspace_root=args.workspace_root or None,
        json_output=args.json,
        task_description=args.task_description or "",
        spec_file=args.spec_file or ""
    )

if __name__ == "__main__":
    main()
