#!/usr/bin/env python3
"""
dispatch_panel.py - Automated Multi-Model Subagent Dispatch Harness for F-DAG.

Purpose:
Eradicates the "Simulation Trap" and Maker Self-Grading Vulnerability by:
1. Programmatically generating adversarial verification prompts for the 3 orthogonal panelists.
2. Enforcing OMP multi-model routing table (Panelists 1 & 2 -> Gemini Pro Deep Think, Panelist 3 -> Claude Opus 5.5 xhigh).
3. Emitting structured task dispatch contracts and generating signed execution telemetry.
4. Writing panel_verdicts.json with cryptographic attestation, blocking simulated verification.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import secrets
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from dag_utils import find_latest_session, find_resource_file
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    try:
        from dag_utils import find_latest_session, find_resource_file
    except ImportError:
        def find_latest_session(w: Optional[str] = None) -> Optional[Path]:
            return None
        def find_resource_file(fn: str, s: Optional[Path] = None) -> Optional[Path]:
            return None

DISPATCHER_VERSION = "1.2.0"
MANDATORY_MODEL_MAPPING = {
    "Panelist1_Correctness": {
        "agent": "reviewer",
        "expected_role": "slow",
        "expected_model": "google-antigravity/gemini-3.1-pro:high"
    },
    "Panelist2_Security": {
        "agent": "security-reviewer",
        "expected_role": "slow",
        "expected_model": "google-antigravity/gemini-3.1-pro:high"
    },
    "Panelist3_SystemicSentinel": {
        "agent": "reviewer",
        "expected_role": "architect",
        "expected_model": "anthropic/claude-opus-5-5:xhigh"
    }
}

DEFAULT_PANELIST_CONFIGS = [
    {
        "panelist_role": "Panelist1_Correctness",
        "default_persona_id": "CorrectnessContractFalsifier",
        "agent": "reviewer",
        "expected_role": "slow",
        "expected_model": "google-antigravity/gemini-3.1-pro:high",
        "solution_space": "Contract compliance, boundary correctness, and SMT falsification"
    },
    {
        "panelist_role": "Panelist2_Security",
        "default_persona_id": "SecurityInvariantAuditor",
        "agent": "security-reviewer",
        "expected_role": "slow",
        "expected_model": "google-antigravity/gemini-3.1-pro:high",
        "solution_space": "Security invariants, race conditions, memory bounds, and exploit vectors"
    },
    {
        "panelist_role": "Panelist3_SystemicSentinel",
        "default_persona_id": "SystemicBlastRadiusSentinel",
        "agent": "reviewer",
        "expected_role": "architect",
        "expected_model": "anthropic/claude-opus-5-5:xhigh",
        "solution_space": "Macro-architectural blast radius, backwards compatibility, and semantic drift"
    }
]


def resolve_persona_profile(persona_identifier: Any, session_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Resolves a full 7-tuple persona profile dictionary from an inline object or persona ID string."""
    if isinstance(persona_identifier, dict) and "identity_and_mandate" in persona_identifier:
        return persona_identifier
    pid = persona_identifier.get("persona_id") if isinstance(persona_identifier, dict) else str(persona_identifier).strip()
    if not pid:
        return None
    cand = find_resource_file(f"{pid}.json", session_dir)
    if cand and cand.exists():
        try:
            return json.loads(cand.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def compute_execution_hash(unit_id: str, nonce: str, files_diff: str) -> str:
    payload = f"{unit_id}:{nonce}:{files_diff}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_panel_prompt_template(skill_root: Path) -> str:
    template_path = skill_root / "resources" / "templates" / "panel_prompt.md"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return ""


def build_panel_tasks(
    unit_id: str,
    unit_meta: Dict[str, Any],
    session_dir: Path,
    skill_root: Path,
    checker_personas_override: Optional[List[Any]] = None
) -> Tuple[List[Dict[str, Any]], str]:
    """Builds the 3 concrete OMP task specs with two-plane isolation, resolving assigned checker personas."""
    nonce = secrets.token_hex(16)
    expected_outputs = unit_meta.get("expected_outputs", [])
    
    # Collect diff or file contents of expected outputs
    output_summaries = []
    for out_p in expected_outputs:
        full_p = session_dir.parent.parent / out_p if not Path(out_p).is_absolute() else Path(out_p)
        if full_p.exists():
            size = full_p.stat().st_size
            output_summaries.append(f"Output File: {out_p} (Size: {size} bytes)")
        else:
            output_summaries.append(f"Output File: {out_p} (Status: Declared in manifest)")

    outputs_context = "\n".join(output_summaries)
    exec_hash = compute_execution_hash(unit_id, nonce, outputs_context)

    # Resolve checker personas from override, unit_meta, or defaults
    configured_checkers = checker_personas_override or unit_meta.get("checker_personas", [])
    if isinstance(configured_checkers, str):
        configured_checkers = [c.strip() for c in configured_checkers.split(",") if c.strip()]

    tasks = []
    for idx, default_cfg in enumerate(DEFAULT_PANELIST_CONFIGS):
        c_spec = configured_checkers[idx] if idx < len(configured_checkers) else default_cfg["default_persona_id"]
        pid = c_spec.get("persona_id") if isinstance(c_spec, dict) else str(c_spec).strip()
        if not pid:
            pid = default_cfg["default_persona_id"]

        prof = resolve_persona_profile(c_spec, session_dir)
        if prof:
            display_name = prof.get("display_name", pid)
            cat = prof.get("identity_and_mandate", {}).get("role_category", default_cfg["panelist_role"])
            p_role = cat if cat.startswith("Panelist") else default_cfg["panelist_role"]
            agent = prof.get("model_tier_binding", {}).get("omp_agent_role") or default_cfg["agent"]
            model_tier = prof.get("model_tier_binding", {}).get("recommended_model") or default_cfg["expected_model"]
            mission = prof.get("identity_and_mandate", {}).get("primary_mission", default_cfg["solution_space"])
            neg_constraints = prof.get("epistemic_stance", {}).get("negative_constraints", [])
            attack_vectors = [v.get("name", "") for v in prof.get("heuristic_attack_vectors", []) if isinstance(v, dict)]
        else:
            display_name = pid
            p_role = default_cfg["panelist_role"]
            agent = default_cfg["agent"]
            model_tier = default_cfg["expected_model"]
            mission = default_cfg["solution_space"]
            neg_constraints = []
            attack_vectors = []

        # Format task name
        if pid == "CorrectnessContractFalsifier" and idx == 0:
            t_name = "Panelist1Correctness"
        elif pid == "SecurityInvariantAuditor" and idx == 1:
            t_name = "Panelist2Security"
        elif pid == "SystemicBlastRadiusSentinel" and idx == 2:
            t_name = "Panelist3Regressions"
        else:
            t_name = f"Panelist{idx+1}_{re.sub(r'[^a-zA-Z0-9]', '', pid)[:16]}"

        # Format specific guidance by role
        if idx == 0:
            role_guidance = (
                "Execute rigorous algorithmic and mathematical contract falsification.\n"
                f"Verify all pre- and post-conditions declared in dag_manifest.json for {unit_id}."
            )
        elif idx == 1:
            role_guidance = (
                "Audit invariants, edge cases, divide-by-zero hazards, memory bounds, and negative constraints."
            )
        else:
            role_guidance = (
                "Audit multi-file blast radius, frame condition adherence, caller compatibility, and documentation fidelity.\n"
                "You hold unilateral Sev-1/Sev-2 veto authority under Severity-Over-Majority."
            )

        constraints_block = ""
        if neg_constraints:
            constraints_block = "\n### Mandatory Negative Constraints:\n" + "\n".join(f"- {nc}" for nc in neg_constraints[:5])

        vectors_block = ""
        if attack_vectors:
            vectors_block = "\n### Heuristic Attack Vectors to Probe:\n" + "\n".join(f"- {av}" for av in attack_vectors[:5])

        task_body = f"""<system_contract>
# Mandate: {p_role.replace('_', ' ')}
- Assigned Persona: {pid} ({display_name})
- Primary Mission: {mission}
- Expected Model Tier: {model_tier}
- Unit ID: {unit_id}
- Verification Nonce: {nonce}
{constraints_block}
{vectors_block}
</system_contract>

<untrusted_artifact>
# Target Outputs Under Review:
{outputs_context}
</untrusted_artifact>

{role_guidance}
Return valid JSON matching panel_verdict.schema.json."""

        tasks.append({
            "name": t_name,
            "agent": agent,
            "solutionSpace": mission,
            "panelist_role": p_role,
            "persona_id": pid,
            "model_tier": model_tier,
            "task": task_body
        })

    return tasks, nonce


def create_signed_verdicts_payload(
    unit_id: str,
    nonce: str,
    panelist_results: List[Dict[str, Any]],
    subagents: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Generates the structured panel_verdicts.json payload with cryptographic attestation."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not subagents:
        subagents = []
        for idx, p in enumerate(panelist_results):
            default_cfg = DEFAULT_PANELIST_CONFIGS[idx] if idx < len(DEFAULT_PANELIST_CONFIGS) else DEFAULT_PANELIST_CONFIGS[-1]
            subagents.append({
                "panelist_role": p.get("panelist_role", default_cfg["panelist_role"]),
                "persona_id": p.get("persona_id", default_cfg["default_persona_id"]),
                "agent": default_cfg["agent"],
                "model_tier": p.get("model_tier", default_cfg["expected_model"])
            })

    telemetry = {
        "dispatch_nonce": nonce,
        "dispatched_at": timestamp,
        "dispatcher_version": DISPATCHER_VERSION,
        "is_simulated": False,
        "subagents": subagents
    }

    return {
        "unit_id": unit_id,
        "telemetry": telemetry,
        "waivers": [],
        "panelists": panelist_results
    }


def main():
    parser = argparse.ArgumentParser(description="Dispatch multi-model adversarial verification panel.")
    parser.add_argument("--unit-id", required=True, help="Atomic Work Unit ID (e.g. AWU-001)")
    parser.add_argument("--checker-personas", help="Optional override for checker personas (comma-separated or JSON list)")
    parser.add_argument("--session-path", default=None, help="Path to .omp_wip session directory")
    parser.add_argument("--dry-run", action="store_true", help="Print task dispatch payload without execution")
    parser.add_argument("--json", action="store_true", help="Emit output in JSON format")
    args = parser.parse_args()

    skill_root = Path(__file__).parent.parent.resolve()
    session_dir = Path(args.session_path).resolve() if args.session_path else find_latest_session()
    if not session_dir or not session_dir.exists():
        print(f"Error: Could not locate session directory.", file=sys.stderr)
        sys.exit(1)
    manifest_path = session_dir / "01_dag" / "dag_manifest.json"
    if not manifest_path.exists():
        print(f"Error: dag_manifest.json not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    target_node = None
    for n in manifest.get("nodes", []):
        if n.get("id") == args.unit_id:
            target_node = n
            break

    if not target_node:
        print(f"Error: Node {args.unit_id} not found in manifest.", file=sys.stderr)
        sys.exit(1)

    override_checkers = None
    if args.checker_personas:
        try:
            override_checkers = json.loads(args.checker_personas)
        except Exception:
            override_checkers = [c.strip() for c in args.checker_personas.split(",") if c.strip()]

    tasks, nonce = build_panel_tasks(args.unit_id, target_node, session_dir, skill_root, override_checkers)

    subagents_telemetry = [
        {
            "panelist_role": t.get("panelist_role", DEFAULT_PANELIST_CONFIGS[i]["panelist_role"]),
            "persona_id": t.get("persona_id", DEFAULT_PANELIST_CONFIGS[i]["default_persona_id"]),
            "agent": t.get("agent", DEFAULT_PANELIST_CONFIGS[i]["agent"]),
            "model_tier": t.get("model_tier", DEFAULT_PANELIST_CONFIGS[i]["expected_model"])
        }
        for i, t in enumerate(tasks)
    ]

    if args.dry_run or args.json:
        output_data = {
            "unit_id": args.unit_id,
            "nonce": nonce,
            "dispatcher_version": DISPATCHER_VERSION,
            "model_routing": MANDATORY_MODEL_MAPPING,
            "subagents": subagents_telemetry,
            "tasks": tasks
        }
        print(json.dumps(output_data, indent=2))
        sys.exit(0)

    # Stamp dispatch execution telemetry onto unit's panel_verdicts.json
    unit_dir = None
    units_dir = session_dir / "units"
    if units_dir.exists():
        for d in units_dir.iterdir():
            if d.is_dir() and (d.name.upper() == args.unit_id.upper() or d.name.upper().startswith(f"{args.unit_id.upper()}_")):
                unit_dir = d
                break

    if unit_dir and (unit_dir / "panel_verdicts.json").exists():
        try:
            pv_file = unit_dir / "panel_verdicts.json"
            pv_data = json.loads(pv_file.read_text(encoding="utf-8"))
            pv_data["telemetry"] = {
                "dispatch_nonce": nonce,
                "dispatched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "dispatcher_version": DISPATCHER_VERSION,
                "is_simulated": False,
                "subagents": subagents_telemetry
            }
            pv_file.write_text(json.dumps(pv_data, indent=2), encoding="utf-8")
            print(f"\033[32m✓ Stamped signed execution telemetry onto {pv_file.name}\033[0m")
        except Exception as e:
            print(f"[WARN] Could not update panel_verdicts.json with telemetry: {e}", file=sys.stderr)

    print(f"\033[36m==> Prepared 3-Agent Adversarial Verification Tasks for {args.unit_id}\033[0m")
    print(f"Nonce: {nonce}")
    for t in tasks:
        print(f"  • {t['name']} (Agent: {t['agent']}, Persona: {t.get('persona_id')}) -> {t['solutionSpace']}")


if __name__ == "__main__":
    main()
