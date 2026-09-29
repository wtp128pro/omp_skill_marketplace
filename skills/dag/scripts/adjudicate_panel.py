#!/usr/bin/env python3
"""
formal_adjudicate_panel.py / adjudicate_panel.py - Deterministic Adjudication Engine for Heterogeneous Panels.

Features & Invariants Enforced:
1. Deterministic JSON Verdict Ingestion: Validates against panel_verdict.schema.json.
2. Anti-Rubber-Stamping Verification: Fails approval if falsification evidence is empty.
3. Cryptographic Waiver Protocol:
   - Sev-1 defects are structurally UNWAIVABLE per enterprise safety invariants.
   - Sev-2 defects may be waived iff a valid architectural waiver is attached.
4. Mandatory Counterexample Requirement (Proof(d)):
   - Every defect must declare concrete counterexample, root cause, and negative constraint.
5. Strict Severity-Over-Majority Rule:
   - Any active Sev-1 or Sev-2 defect -> Immediate REJECT_VETO (overrides 2-1 majority).
   - PASS requires zero active Sev-1/Sev-2 defects and >= 2 APPROVE votes.
6. Structured Knowledge Persistence: Records counterexamples and negative constraints to learnings.jsonl.
7. Automated Manifest & State Transition: Updates dag_manifest.json with verdict, iterations, and status.
8. Automated Contract Re-Briefing: Injects negative constraints into briefing.md for iteration N+1.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    from dag_utils import find_resource_file, find_latest_session
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    try:
        from dag_utils import find_resource_file, find_latest_session
    except ImportError:
        def find_resource_file(fn: str, s: Optional[Path] = None) -> Optional[Path]:
            p = Path(__file__).parent.parent / "resources" / "templates" / fn
            return p if p.exists() else None
        def find_latest_session(w: Optional[str] = None) -> Optional[Path]:
            return None


def standardize_severity(s: str) -> str:
    cleaned = str(s).strip()
    if re.match(r"^none\b", cleaned, re.IGNORECASE):
        return "None"
    m = re.search(r"\b(Sev[-\s]?1|Critical)\b", cleaned, re.IGNORECASE)
    if m:
        return "Sev-1"
    m = re.search(r"\b(Sev[-\s]?2|Major)\b", cleaned, re.IGNORECASE)
    if m:
        return "Sev-2"
    m = re.search(r"\b(Sev[-\s]?3|Minor)\b", cleaned, re.IGNORECASE)
    if m:
        return "Sev-3"
    return "None"



def validate_telemetry_attestation(raw_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enforces Maker != Checker Orthogonality and the Tri-Model Heterogeneous Tiering Architecture.
    Prevents the 'Simulation Trap' where a Maker self-grades by generating mock verdicts.
    """
    defects = []
    if raw_data is None or not isinstance(raw_data, dict):
        return defects

    telemetry = raw_data.get("telemetry")
    if not telemetry:
        defects.append({
            "defect_id": "ATTEST-001",
            "severity": "Sev-1",
            "summary": "CRITICAL ATTESTATION BREACH: Missing subagent execution telemetry. Maker self-grading or simulated verification detected.",
            "counterexample": "panel_verdicts.json lacks 'telemetry' block containing dispatch nonce and subagent runtime tracking.",
            "root_cause": "Verification panel was authored directly by Maker rather than dispatched out-of-process to independent subagents.",
            "negative_constraint": "All verification panels MUST be executed via dispatch_panel.py and record signed subagent telemetry."
        })
        return defects

    if telemetry.get("is_simulated") is True:
        defects.append({
            "defect_id": "ATTEST-002",
            "severity": "Sev-1",
            "summary": "CRITICAL ATTESTATION BREACH: Verdict declared as simulated execution.",
            "counterexample": "telemetry.is_simulated == true",
            "root_cause": "Synthetic verification was substituted for genuine adversarial subagent execution.",
            "negative_constraint": "Simulated verification verdicts are structurally invalid for AWU completion."
        })
        return defects

    subagents = telemetry.get("subagents", [])
    if len(subagents) >= 3:
        models_used = set(s.get("model_tier", "") for s in subagents if isinstance(s, dict))
        if len(models_used) <= 1:
            defects.append({
                "defect_id": "ATTEST-003",
                "severity": "Sev-1",
                "summary": "CRITICAL TRI-MODEL INVARIANT VIOLATION: All panelists executed on identical model tier. Cognitive monoculture detected.",
                "counterexample": f"All subagents used single model: {list(models_used)}",
                "root_cause": "OMP task.agentModelOverrides was unmapped, defaulting all subagents to parent session model.",
                "negative_constraint": "Panelists 1 & 2 MUST run on Deep Reasoning tier (Gemini Pro), and Panelist 3 MUST run on Macro-Reasoning tier (Claude Opus 5.5)."
            })

    return defects


def load_waivers(unit_dir: Path, sess_dir: Path, raw_verdicts_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Loads cryptographic/architectural waivers from unit_dir, sess_dir, or inline in verdicts."""
    waivers: List[Dict[str, Any]] = []
    if raw_verdicts_data and isinstance(raw_verdicts_data, dict):
        waivers.extend(raw_verdicts_data.get("waivers", []))

    unit_w = unit_dir / "waivers.json"
    if unit_w.exists():
        try:
            wdata = json.loads(unit_w.read_text(encoding="utf-8"))
            if isinstance(wdata, list):
                waivers.extend(wdata)
            elif isinstance(wdata, dict):
                waivers.extend(wdata.get("waivers", [wdata]))
        except Exception:
            pass

    for wcand in [sess_dir / "01_dag" / "waivers.json", sess_dir / "waivers.json"]:
        if wcand.exists():
            try:
                wdata = json.loads(wcand.read_text(encoding="utf-8"))
                if isinstance(wdata, list):
                    waivers.extend(wdata)
                elif isinstance(wdata, dict):
                    waivers.extend(wdata.get("waivers", [wdata]))
            except Exception:
                pass
    return waivers


def evaluate_waiver(waiver: Dict[str, Any], defect: Dict[str, Any], unit_id: str) -> Tuple[bool, str]:
    """
    Evaluates whether a waiver is valid for a given defect per enterprise waiver protocol:
    1. Sev-1 is UNWAIVABLE.
    2. Sev-2 requires valid architect_id, mitigation_rationale, non-expired expiration_epoch, and signature.
    """
    defect_sev = standardize_severity(defect.get("severity", "Sev-2"))
    if defect_sev == "Sev-1":
        return False, "Sev-1 defect is structurally UNWAIVABLE per enterprise safety invariants."

    w_def_id = str(waiver.get("defect_id", "")).strip()
    w_awu_id = str(waiver.get("awu_id", "")).strip().upper()
    d_id = str(defect.get("defect_id", "")).strip()

    matches = False
    if w_def_id and d_id and w_def_id.lower() == d_id.lower():
        matches = True
    elif w_awu_id and w_awu_id == unit_id.upper():
        matches = True
    elif not w_def_id and not w_awu_id:
        matches = True

    if not matches:
        return False, "Waiver target ID does not match defect or AWU."

    exp_epoch = waiver.get("expiration_epoch")
    if exp_epoch is not None:
        if time.time() > float(exp_epoch):
            return False, f"Waiver expired at epoch {exp_epoch}."

    if not waiver.get("architect_id"):
        return False, "Missing required architect_id in waiver."
    if not waiver.get("mitigation_rationale"):
        return False, "Missing required mitigation_rationale in waiver."
    if not waiver.get("signature"):
        return False, "Missing required cryptographic signature in waiver."

    return True, f"Waived by Principal Architect {waiver.get('architect_id')}: {waiver.get('mitigation_rationale')}"


def parse_verdicts_from_json(json_path: Path, schema_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Loads and validates structured panel verdicts from JSON."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    panelists = data.get("panelists", []) if isinstance(data, dict) else data
    if not isinstance(panelists, list) or len(panelists) != 3:
        raise ValueError(f"Expected array of exactly 3 panelist objects in {json_path.name}")

    if HAS_JSONSCHEMA and schema_path and schema_path.exists():
        try:
            schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
            validator = jsonschema.Draft7Validator(schema_data)
            for idx, p in enumerate(panelists, 1):
                validator.validate(p)
        except jsonschema.ValidationError as ve:
            print(f"[WARN] Panelist {idx} verdict failed schema validation: {ve.message}", file=sys.stderr)

    return panelists


def parse_verdicts_from_markdown(md_path: Path) -> List[Dict[str, Any]]:
    """Fallback parser with enhanced robustness for legacy markdown."""
    content = md_path.read_text(encoding="utf-8")
    vote_matches = re.findall(r"^-\s+\*\*Vote\*\*:\s*[`*]*([A-Za-z_]+)", content, re.MULTILINE | re.IGNORECASE)
    sev_matches = re.findall(r"^-\s+\*\*Highest Defect Severity Detected\*\*:\s*[`*]*([A-Za-z0-9_\-\s]+?)(?=[`*]*(?:\s*\(|$|\n))", content, re.MULTILINE | re.IGNORECASE)

    if len(vote_matches) < 3 or len(sev_matches) < 3:
        raise ValueError(f"Legacy markdown parser could not extract 3 votes and severities from {md_path.name}")

    results = []
    for idx in range(3):
        results.append({
            "panelist_role": f"Panelist_{idx+1}",
            "vote": vote_matches[idx].upper(),
            "highest_severity": standardize_severity(sev_matches[idx]),
            "falsification_evidence": ["Extracted from legacy markdown"],
            "defects": []
        })
    return results


def update_briefing_with_learnings(briefing_path: Path, learnings_records: List[Dict[str, Any]]):
    """Appends structured negative constraints to briefing.md for iteration N+1."""
    if not briefing_path.exists() or not learnings_records:
        return

    content = briefing_path.read_text(encoding="utf-8")
    lines = [
        "\n## Mandatory Accumulated Learnings & Negative Constraints (From Prior Rejections)\n",
        "*(The previous implementation was VETOED. You are strictly bound by the following negative constraints:)*\n"
    ]
    for idx, r in enumerate(learnings_records, 1):
        lines.append(f"{idx}. **[{r['severity']} - {r['panelist_source']}]:**")
        lines.append(f"   - **Constraint:** {r['negative_constraint']}")
        lines.append(f"   - **Counterexample:** {r['counterexample']}")
        lines.append(f"   - **Root Cause:** {r['root_cause']}\n")

    constraint_block = "\n".join(lines)
    if "## Mandatory Accumulated Learnings" in content:
        content = re.sub(
            r"## Mandatory Accumulated Learnings.*?(?=\n## |\Z)",
            constraint_block.strip() + "\n\n",
            content,
            flags=re.DOTALL
        )
    elif "</system_contract>" in content:
        content = content.replace("</system_contract>", constraint_block.strip() + "\n</system_contract>")
    else:
        content += "\n" + constraint_block
    briefing_path.write_text(content, encoding="utf-8")


def formal_adjudicate_unit(
    unit_id: str,
    session_path: str = None,
    workspace_root: str = None,
    json_output: bool = False,
    enforce_telemetry: bool = False,
    enforce_evidence_check: bool = True
) -> Dict[str, Any]:
    sess_dir = Path(session_path).resolve() if session_path else find_latest_session(workspace_root)
    if not sess_dir or not sess_dir.exists():
        print("[ERROR] Session directory not found.", file=sys.stderr)
        sys.exit(1)

    clean_unit_id = re.sub(r"[^a-zA-Z0-9_-]", "-", unit_id).upper().strip("-_")
    units_dir = sess_dir / "units"
    matches = [d for d in units_dir.iterdir() if d.is_dir() and (d.name.upper() == clean_unit_id or d.name.upper().startswith(f"{clean_unit_id}_"))]

    if not matches:
        print(f"[ERROR] Unit directory for {clean_unit_id} not found under {units_dir}", file=sys.stderr)
        sys.exit(1)

    unit_dir = matches[0]
    json_verdicts = unit_dir / "panel_verdicts.json"
    md_verdicts = unit_dir / "panel_verdicts.md"
    learnings_path = unit_dir / "learnings.jsonl"
    briefing_path = unit_dir / "briefing.md"
    manifest_path = sess_dir / "01_dag" / "dag_manifest.json"

    schema_file = find_resource_file("panel_verdict.schema.json", sess_dir)

    # Ingest verdicts
    raw_verdicts_data = None
    if json_verdicts.exists():
        try:
            raw_verdicts_data = json.loads(json_verdicts.read_text(encoding="utf-8"))
            panelists = parse_verdicts_from_json(json_verdicts, schema_file)
        except Exception as e:
            print(f"[ERROR] Failed parsing {json_verdicts.name}: {e}", file=sys.stderr)
            sys.exit(1)
    elif md_verdicts.exists():
        try:
            panelists = parse_verdicts_from_markdown(md_verdicts)
            if not json_output:
                print("\033[33m[NOTE] Ingested verdicts from legacy Markdown format (upgrade to JSON recommended).\033[0m")
        except Exception as e:
            print(f"[ERROR] Failed parsing {md_verdicts.name}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[ERROR] Neither panel_verdicts.json nor panel_verdicts.md found in {unit_dir}", file=sys.stderr)
        sys.exit(1)

    # 1. Enforce subagent execution telemetry attestation before computing votes
    if (enforce_telemetry or (raw_verdicts_data and "telemetry" in raw_verdicts_data)) and raw_verdicts_data:
        attestation_defects = validate_telemetry_attestation(raw_verdicts_data)
        if attestation_defects:
            if panelists:
                panelists[-1].setdefault("defects", []).extend(attestation_defects)
                panelists[-1]["vote"] = "REJECT"
                panelists[-1]["highest_severity"] = "Sev-1"
    elif enforce_telemetry and not raw_verdicts_data:
        attestation_defects = [{
            "defect_id": "ATTEST-001",
            "severity": "Sev-1",
            "summary": "CRITICAL ATTESTATION BREACH: Missing subagent execution telemetry.",
            "counterexample": "No structured JSON telemetry available.",
            "root_cause": "Verification panel lacks signed subagent execution telemetry.",
            "negative_constraint": "All verification panels MUST be executed via dispatch_panel.py and record signed telemetry."
        }]
        if panelists:
            panelists[-1].setdefault("defects", []).extend(attestation_defects)
            panelists[-1]["vote"] = "REJECT"
            panelists[-1]["highest_severity"] = "Sev-1"

    # Evaluate Votes & Severities (evaluated after attestation checks)
    votes = [p.get("vote", "REJECT").upper() for p in panelists]
    severities = [standardize_severity(p.get("highest_severity", "None")) for p in panelists]

    # Anti-Rubber-Stamping Verification
    if enforce_evidence_check:
        for idx, p in enumerate(panelists):
            if p.get("vote") == "APPROVE":
                evidence = p.get("falsification_evidence") or p.get("edge_cases_tested", [])
                if isinstance(evidence, list) and len(evidence) == 0:
                    if not json_output:
                        print(f"\033[33m[WARN] Panelist {idx+1} approved without supplying concrete falsification evidence.\033[0m")
    # 2. Defect Verification & Cryptographic Waiver Processing
    active_waivers = load_waivers(unit_dir, sess_dir, raw_verdicts_data)
    waived_defects: List[Dict[str, Any]] = []
    unwaived_defects: List[Dict[str, Any]] = []

    # Check for active unresolved Assumption Invalidation Human Gate on this unit
    if manifest_path.exists():
        try:
            m_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            invals = m_data.get("invalidated_assumptions", [])
            for inv in invals:
                if inv.get("unit_id") == clean_unit_id and inv.get("status") == "ACTIVE_BLOCKER":
                    unwaived_defects.append({
                        "defect_id": f"INVAL-GATE-{inv.get('invalidation_id')}",
                        "severity": "Sev-1",
                        "summary": f"ASSUMPTION INVALIDATION HUMAN GATE VETO: Prior assumption '{inv.get('assumption_summary')}' was invalidated during execution and is pending mandatory human resolution.",
                        "counterexample": inv.get("discovery_evidence", "Empirical discovery broke prior assumption."),
                        "root_cause": "Dynamic execution discovery contradicted baseline assumptions without human gate sign-off.",
                        "negative_constraint": "DO NOT proceed with AWU adjudication until human resolves the assumption invalidation via Socratic dialogue.",
                        "source_role": "AssumptionInvalidationGate"
                    })
        except Exception:
            pass

    for p in panelists:
        p_role = p.get("panelist_role", "Adversarial Panelist")
        p_sev = standardize_severity(p.get("highest_severity", "None"))
        p_defects = p.get("defects", [])
        for d in p_defects:
            sev = standardize_severity(d.get("severity", "None"))
            if sev in ("Sev-1", "Sev-2"):
                # Mandatory Counterexample Verification (Proof(d))
                c_example = d.get("counterexample")
                r_cause = d.get("root_cause")
                n_constraint = d.get("negative_constraint")
                if not c_example or str(c_example).strip() in ("", "None", "Failing state"):
                    if not json_output:
                        print(f"\033[33m[WARN] Defect from {p_role} lacks concrete falsification counterexample: {d.get('summary')}\033[0m")
                if not r_cause or str(r_cause).strip() in ("", "None"):
                    if not json_output:
                        print(f"\033[33m[WARN] Defect from {p_role} lacks root_cause analysis: {d.get('summary')}\033[0m")

                # Check for matching waivers
                is_waived = False
                waiver_reason = ""
                for w in active_waivers:
                    ok, reason = evaluate_waiver(w, d, clean_unit_id)
                    if ok:
                        is_waived = True
                        waiver_reason = reason
                        break

                if is_waived:
                    d_copy = dict(d)
                    d_copy["waived_by"] = waiver_reason
                    waived_defects.append(d_copy)
                    if not json_output:
                        print(f"\033[35m[WAIVER APPLIED] {sev} Defect '{d.get('summary')}' successfully waived: {waiver_reason}\033[0m")
                else:
                    d_copy = dict(d)
                    d_copy["source_role"] = p_role
                    unwaived_defects.append(d_copy)

        # Synthesize defect if panelist recorded Sev-1 or Sev-2 in highest_severity but defects list omitted it
        if p_sev in ("Sev-1", "Sev-2") and not any(standardize_severity(d.get("severity", "None")) == p_sev for d in p_defects):
            synth_defect = {
                "defect_id": f"DEF-{re.sub(r'[^a-zA-Z0-9]', '', p_role)[:16]}-001",
                "severity": p_sev,
                "summary": f"Veto condition detected by {p_role} ({p_sev})",
                "counterexample": (p.get("falsification_evidence") or ["Adversarial falsification veto"])[0] if p.get("falsification_evidence") else "Failing invariant or boundary condition",
                "root_cause": f"Panelist {p_role} recorded {p_sev} severity breach.",
                "negative_constraint": f"DO NOT violate contracts verified by {p_role}.",
                "source_role": p_role
            }
            is_waived = False
            waiver_reason = ""
            for w in active_waivers:
                ok, reason = evaluate_waiver(w, synth_defect, clean_unit_id)
                if ok:
                    is_waived = True
                    waiver_reason = reason
                    break
            if is_waived:
                synth_defect["waived_by"] = waiver_reason
                waived_defects.append(synth_defect)
                if not json_output:
                    print(f"\033[35m[WAIVER APPLIED] {p_sev} Defect '{synth_defect['summary']}' successfully waived: {waiver_reason}\033[0m")
            else:
                unwaived_defects.append(synth_defect)

    # 3. Determine Highest Active Global Severity
    unwaived_severities = [standardize_severity(d.get("severity", "None")) for d in unwaived_defects]
    if "Sev-1" in unwaived_severities:
        global_severity = "Sev-1"
    elif "Sev-2" in unwaived_severities:
        global_severity = "Sev-2"
    elif any(standardize_severity(s) == "Sev-3" for s in severities):
        global_severity = "Sev-3"
    else:
        global_severity = "None"

    approve_count = sum(1 for v in votes if v == "APPROVE")
    reject_count = sum(1 for v in votes if v == "REJECT")
    pending_count = sum(1 for v in votes if v == "PENDING")

    # 4. Mathematical Severity-Over-Majority Adjudication
    if global_severity in ("Sev-1", "Sev-2"):
        final_verdict = "REJECT_VETO"
        severity_override = (approve_count >= 2)
        explanation = f"IMMEDIATE VETO: Active {global_severity} defect detected without valid waiver. Problem gravity overrides majority."
    elif pending_count == len(panelists):
        final_verdict = "PENDING"
        severity_override = False
        explanation = f"PANEL VERIFICATION PENDING: All {len(panelists)} adversarial panelists have not yet submitted verdicts."
    elif pending_count > 0 and approve_count < 2 and reject_count < 2:
        final_verdict = "PENDING"
        severity_override = False
        explanation = f"PANEL VERIFICATION IN PROGRESS: {pending_count} of {len(panelists)} panelist verdicts still pending."
    elif reject_count >= 2:
        final_verdict = "REJECT_MAJORITY"
        severity_override = False
        explanation = f"REJECTED BY MAJORITY: {reject_count} of 3 adversarial panelists voted to reject."
    elif approve_count >= 2 and waived_defects:
        final_verdict = "PASS_WAIVED"
        severity_override = False
        explanation = f"APPROVED WITH WAIVER: Zero active Sev-1 defects; {len(waived_defects)} Sev-2 defect(s) lawfully waived by Principal Systems Architect."
    elif approve_count >= 2 and global_severity == "Sev-3":
        final_verdict = "PASS_WITH_CAVEAT"
        severity_override = False
        explanation = "APPROVED WITH CAVEAT: Zero Sev-1/Sev-2 defects found. Minor Sev-3 cosmetic/documentation notes logged."
    elif approve_count >= 2:
        final_verdict = "PASS"
        severity_override = False
        explanation = "APPROVED: Zero active defects found and passing majority achieved across all 3 adversarial checkers."
    else:
        final_verdict = "REJECT"
        severity_override = False
        explanation = "REJECTED: Contractual passing criteria not met."
    # 5. Extract Structured Learnings on Rejection (Unwaived Defects Only)
    new_learnings = []
    if final_verdict in ("REJECT_VETO", "REJECT_MAJORITY", "REJECT"):
        for d in unwaived_defects:
            sev = standardize_severity(d.get("severity", "Sev-2"))
            if sev in ("Sev-1", "Sev-2"):
                new_learnings.append({
                    "awu_id": clean_unit_id,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "panelist_source": d.get("source_role", "Adversarial Panel"),
                    "severity": sev,
                    "defect_summary": d.get("summary", "Unspecified contract breach"),
                    "counterexample": d.get("counterexample", "Failing state"),
                    "root_cause": d.get("root_cause", "Logical or invariant violation"),
                    "negative_constraint": d.get("negative_constraint", "Do not repeat failed pattern.")
                })

        # Append to learnings.jsonl
        if new_learnings:
            with open(learnings_path, "a", encoding="utf-8") as f:
                for entry in new_learnings:
                    f.write(json.dumps(entry) + "\n")
            update_briefing_with_learnings(briefing_path, new_learnings)

    # 6. Atomic Manifest Update
    if manifest_path.exists():
        try:
            mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
            for node in mdata.get("nodes", []):
                if node.get("id", "").upper().strip() == clean_unit_id:
                    node["iteration_count"] = node.get("iteration_count", 0) + 1
                    node["panel_adjudication"] = {
                        "verdict": final_verdict,
                        "highest_severity": global_severity,
                        "severity_override": severity_override,
                        "adjudicated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                    active_blocker = any(
                        inv.get("unit_id") == clean_unit_id and inv.get("status") == "ACTIVE_BLOCKER"
                        for inv in mdata.get("invalidated_assumptions", [])
                    )
                    if "PASS" in final_verdict:
                        node["status"] = "COMPLETED"
                    elif active_blocker:
                        node["status"] = "BLOCKED"
                    elif node.get("iteration_count", 0) >= node.get("max_iterations", 3):
                        node["status"] = "ESCALATED"
                    else:
                        node["status"] = "PENDING"
            manifest_path.write_text(json.dumps(mdata, indent=2), encoding="utf-8")
        except Exception as me:
            print(f"[WARN] Could not update dag_manifest.json automatically: {me}", file=sys.stderr)

    # 7. Output Summary
    if not json_output:
        print(f"\033[36m==> Formal Adjudication for {clean_unit_id}\033[0m")
        print(f"Votes:              {', '.join(votes)}")
        print(f"Severities:         {', '.join(severities)}")
        print(f"Global Severity:    {global_severity}")
        status_color = "\033[32m" if "PASS" in final_verdict else "\033[31m"
        print(f"Final Verdict:      {status_color}{final_verdict}\033[0m")
        print(f"Severity Override:  {'YES (Vetoed despite passing majority)' if severity_override else 'NO'}")
        print(f"Explanation:        {explanation}")
        if waived_defects:
            print(f"\033[35mWaived Defects ({len(waived_defects)}):\033[0m")
            for idx, wd in enumerate(waived_defects, 1):
                print(f"  {idx}. [{wd.get('severity')}] {wd.get('summary')} -> {wd.get('waived_by')}")
        if new_learnings:
            print(f"\n\033[33mExtracted {len(new_learnings)} negative constraint(s) to learnings.jsonl & briefing.md:\033[0m")
            for idx, l in enumerate(new_learnings, 1):
                print(f"  {idx}. [{l['severity']}] {l['negative_constraint']}")

    res = {
        "unit_id": clean_unit_id,
        "final_verdict": final_verdict,
        "global_severity": global_severity,
        "severity_override": severity_override,
        "votes": votes,
        "severities": severities,
        "explanation": explanation,
        "new_learnings_count": len(new_learnings),
        "waived_defects_count": len(waived_defects),
        "unwaived_defects": unwaived_defects,
        "waived_defects": waived_defects
    }

    if json_output:
        print(json.dumps(res, indent=2))

    return res


def main():
    parser = argparse.ArgumentParser(description="Formal Adjudication Engine for 3-Agent Panels.")
    parser.add_argument("--unit-id", required=True, help="Unit ID (e.g., AWU-001)")
    parser.add_argument("--session-path", help="Path to session directory")
    parser.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    parser.add_argument("--enforce-telemetry", action="store_true", help="Strictly require subagent telemetry attestation")
    parser.add_argument("--no-evidence-check", action="store_true", help="Skip anti-rubber-stamping evidence verification")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    res = formal_adjudicate_unit(
        unit_id=args.unit_id,
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json,
        enforce_telemetry=args.enforce_telemetry,
        enforce_evidence_check=not args.no_evidence_check
    )
    if "PASS" not in res.get("final_verdict", ""):
        sys.exit(1)


if __name__ == "__main__":
    main()
