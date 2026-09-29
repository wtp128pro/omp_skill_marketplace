#!/usr/bin/env python3
"""
formal_scaffold_unit.py / scaffold_dag_unit.py - Formal Atomic Work Unit Scaffolder & Lifecycle Manager.

Features & Invariants Enforced:
1. Instantiates complete unit directory under .omp_wip/<session>/units/<UnitId>_<Slug>/
2. Generates:
   - briefing.md: Human-readable contract with Two-Plane Structural Envelope (<system_contract>)
   - briefing.json: Machine-verifiable contract with pre/post predicates and modifies frame sets
   - panel_verdicts.json: Pre-populated 3-agent template conforming to panel_verdict.schema.json + waivers: []
   - learnings.jsonl: Initialized persistent negative constraints log
   - debriefing.md: Post-execution summary template
3. Automatically links with dag_manifest.json (syncs metadata, inputs, outputs, frame conditions).
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from dag_utils import find_latest_session, find_resource_file
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    try:
        from dag_utils import find_latest_session, find_resource_file
    except ImportError:
        def find_latest_session(workspace_root: Optional[str] = None) -> Optional[Path]:
            search_root = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
            for parent in [search_root] + list(search_root.parents):
                wip_dir = parent / ".omp_wip"
                if wip_dir.is_dir():
                    sessions = [d for d in wip_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
                    if sessions:
                        sessions.sort(key=lambda x: x.name, reverse=True)
                        return sessions[0]
            return None
        def find_resource_file(fn: str, s: Optional[Path] = None) -> Optional[Path]:
            p = Path(__file__).parent.parent / "resources" / "templates" / fn
            return p if p.exists() else None


def formal_scaffold_unit(
    unit_id: str,
    slug: str = "",
    title: str = "",
    maker_persona: str = "",
    checker_personas: List[str] = None,
    dependencies: List[str] = None,
    inputs: List[str] = None,
    expected_outputs: List[str] = None,
    modifies: List[str] = None,
    tier: str = "standard",
    session_path: str = None,
    workspace_root: str = None,
    json_output: bool = False
) -> Dict[str, Any]:
    sess_dir = Path(session_path).resolve() if session_path else find_latest_session(workspace_root)
    if not sess_dir or not sess_dir.exists():
        print("[ERROR] Session directory not found.", file=sys.stderr)
        sys.exit(1)

    clean_unit_id = re.sub(r"[^a-zA-Z0-9_-]", "-", unit_id).upper().strip("-_")
    manifest_path = sess_dir / "01_dag" / "dag_manifest.json"

    manifest_node = None
    manifest_data = None
    if manifest_path.exists():
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for n in manifest_data.get("nodes", []):
                if str(n.get("id", "")).strip().upper() == clean_unit_id:
                    manifest_node = n
                    break
        except Exception:
            pass

    # Populate from manifest if available
    if manifest_node:
        slug = slug or manifest_node.get("slug", "")
        title = title or manifest_node.get("title", "")
        maker_val = manifest_node.get("assigned_maker_persona", {})
        maker_persona = maker_persona or (maker_val.get("persona_id") if isinstance(maker_val, dict) else str(maker_val))
        dependencies = dependencies or manifest_node.get("dependencies", [])
        inputs = inputs or manifest_node.get("inputs", [])
        expected_outputs = expected_outputs or manifest_node.get("expected_outputs", [])
        tier = tier or manifest_node.get("tier", "standard")
        frame_spec = manifest_node.get("frame_conditions", {})
        modifies = modifies or frame_spec.get("modifies", expected_outputs)

    slug = slug or f"unit-{clean_unit_id.lower()}"
    title = title or f"Work Unit {clean_unit_id}"
    maker_persona = maker_persona or "PrincipalSystemsMaker"
    modifies = modifies or expected_outputs or []
    dependencies = dependencies or []
    inputs = inputs or []
    expected_outputs = expected_outputs or modifies

    unit_dirname = f"{clean_unit_id}_{slug}"
    unit_dir = sess_dir / "units" / unit_dirname
    unit_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write briefing.json (Machine-readable formal contract)
    briefing_json_data = {
        "unit_id": clean_unit_id,
        "title": title,
        "tier": tier,
        "assigned_maker_persona": maker_persona,
        "contracts": {
          "pre_conditions": [],
          "post_conditions": [],
          "invariants": []
        },
        "inputs": inputs,
        "expected_outputs": expected_outputs,
        "frame_conditions": {
          "modifies": modifies,
          "immutable": []
        }
    }
    (unit_dir / "briefing.json").write_text(json.dumps(briefing_json_data, indent=2), encoding="utf-8")

    # 2. Write briefing.md with Two-Plane Isolation Structural Envelope
    briefing_md_content = f"""<system_contract integrity="awu:{clean_unit_id}">
# Atomic Work Unit Briefing: {clean_unit_id} - {title}

## 1. Execution Metadata
- **AWU Identifier**: `{clean_unit_id}`
- **Assigned Maker Persona**: `{maker_persona}`
- **Execution Tier**: `{tier}`
- **Iteration Index**: 1 of 3
- **Prerequisite Units**: {dependencies or 'None'}

---

## 2. Mission & Objective
Execute work unit {clean_unit_id} adhering to declared contracts and frame conditions.

---

## 3. Strict Scope Boundaries & Two-Plane Isolation
### IN-SCOPE (Modifies Frame Set)
{chr(10).join(f"- `{m}`" for m in modifies) if modifies else "- Explicit deliverables declared in manifest"}

### OUT-OF-SCOPE & NEGATIVE CONSTRAINTS
- NEVER modify files outside declared frame_conditions.modifies (triggers Sev-1 Frame Breach Veto).
- NEVER introduce speculative future abstractions, unused configuration parameters, or goldplating.
- NEVER bypass or suppress failing unit tests; resolve the root cause.
- All public APIs must provide strict parameter typings, docstrings, and pre/post-conditions.

---

## 4. Verification Criteria
- [ ] Implement deliverables matching declared expected_outputs.
- [ ] Unit tests pass with exit code 0.
- [ ] Zero frame condition breaches audited via frame_condition_auditor.py.
- [ ] 3-agent adversarial panel approval (Severity-Over-Majority rule enforced).
</system_contract>
"""
    (unit_dir / "briefing.md").write_text(briefing_md_content, encoding="utf-8")

    # 3. Write panel_verdicts.json template with waivers support
    panel_verdicts_template = {
      "unit_id": clean_unit_id,
      "waivers": [],
      "panelists": [
        {
          "panelist_role": "Panelist1_Correctness",
          "persona_id": "CorrectnessContractFalsifier",
          "model_tier": "google-antigravity/gemini-3.1-pro:high",
          "vote": "PENDING",
          "highest_severity": "None",
          "falsification_evidence": ["Initial scaffolding pending adversarial panel verification."],
          "defects": []
        },
        {
          "panelist_role": "Panelist2_Security",
          "persona_id": "SecurityInvariantAuditor",
          "model_tier": "google-antigravity/gemini-3.1-pro:high",
          "vote": "PENDING",
          "highest_severity": "None",
          "falsification_evidence": ["Initial scaffolding pending adversarial panel verification."],
          "defects": []
        },
        {
          "panelist_role": "Panelist3_SystemicSentinel",
          "persona_id": "SystemicBlastRadiusSentinel",
          "model_tier": "anthropic/claude-opus-5-5:xhigh",
          "vote": "PENDING",
          "highest_severity": "None",
          "falsification_evidence": ["Initial scaffolding pending adversarial panel verification."],
          "defects": []
        }
      ]
    }
    (unit_dir / "panel_verdicts.json").write_text(json.dumps(panel_verdicts_template, indent=2), encoding="utf-8")

    # 4. Write empty learnings.jsonl
    (unit_dir / "learnings.jsonl").write_text("", encoding="utf-8")

    # 5. Write debriefing.md template
    debriefing_template = f"""# Atomic Work Unit Debriefing: {clean_unit_id} - {title}

## 1. Execution Summary
- **AWU Identifier**: `{clean_unit_id}`
- **Final Status**: PENDING
- **Maker Persona**: `{maker_persona}`

## 2. Deliverables & Modified Artifacts
{chr(10).join(f"- `{o}`" for o in expected_outputs)}

## 3. Verification Evidence
- Automated test output pending.
"""
    (unit_dir / "debriefing.md").write_text(debriefing_template, encoding="utf-8")


    # Register into manifest if not already present
    if manifest_data is not None and not manifest_node:
        new_node = {
            "id": clean_unit_id,
            "slug": slug,
            "title": title,
            "tier": tier,
            "status": "PENDING",
            "assigned_maker_persona": maker_persona,
            "checker_personas": [
                "CorrectnessContractFalsifier",
                "SecurityInvariantAuditor",
                "SystemicBlastRadiusSentinel"
            ],
            "dependencies": dependencies,
            "inputs": inputs,
            "expected_outputs": expected_outputs,
            "frame_conditions": {
                "modifies": modifies or expected_outputs or ["src/**"],
                "immutable": []
            },
            "iteration_count": 0,
            "max_iterations": 3
        }
        manifest_data.setdefault("nodes", []).append(new_node)
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    if not json_output:
        print(f"\033[36m==> Scaffolded AWU {clean_unit_id} in: {unit_dir}\033[0m")
        print(f"  ✓ briefing.json & briefing.md created (with Two-Plane Isolation)")
        print(f"  ✓ panel_verdicts.json template instantiated (with Cryptographic Waiver support)")
        print(f"  ✓ learnings.jsonl initialized")
        print(f"  ✓ debriefing.md scaffolded")

    res = {
        "unit_id": clean_unit_id,
        "unit_dir": str(unit_dir),
        "slug": slug,
        "title": title
    }
    if json_output:
        print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formal AWU Scaffolder & Lifecycle Manager.")
    parser.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    parser.add_argument("--slug", help="URL-safe slug")
    parser.add_argument("--title", help="Human-readable title")
    parser.add_argument("--maker-persona", help="Assigned Maker persona ID")
    parser.add_argument("--session-path", help="Path to active session")
    parser.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    formal_scaffold_unit(
        unit_id=args.unit_id,
        slug=args.slug,
        title=args.title,
        maker_persona=args.maker_persona,
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json
    )
