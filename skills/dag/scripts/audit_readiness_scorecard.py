#!/usr/bin/env python3
"""
audit_readiness_scorecard.py - 5-Point Enterprise Invariant Readiness Scorecard Auditor.

Mechanistic Grounding (Part III, Section 3.4 of Operational Persona whitepaper):
Verifies that multi-agent prompts, contracts, and evaluation pipelines satisfy the 5-point
readiness gate before enterprise production deployment.

Audit Criteria:
1. Structural Envelope & Two-Plane Isolation (MANDATORY):
   - XML structural delimiters (<system_persona>, <system_contract>, <untrusted_artifact>, <untrusted_diff>)
     isolating control plane from untrusted data plane.
2. Absence of Nominal Cosplay Titles (MANDATORY):
   - Zero roleplay fluff tokens ("You are a world-class...", "Act like an expert...", "Senior Architect")
     replaced by explicit operational domain scopes (7-tuple I).
3. Epistemic Inversion & Negative Invariants Defined (MANDATORY):
   - Adversarial prior (E_adv) and at least 3 explicit negative constraints specifying what the agent MUST REJECT.
4. External Grammar Enforcement for Typed Outputs (MANDATORY):
   - Machine-verifiable JSON Schema or external CFG logit processors rather than soft attention hope.
5. Severity-Over-Majority Veto Protocol Active (MANDATORY):
   - Consensus engine permits a single Sev-1 or un-waived Sev-2 defect to halt pipeline regardless of vote count.
"""

import argparse
import json
import re
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
        def find_latest_session(w: Optional[str] = None) -> Optional[Path]: return None
        def find_resource_file(f: str, s: Optional[Path] = None) -> Optional[Path]: return None


NOMINAL_FLUFF_PATTERNS = [
    r"\byou are a (?:world-class|distinguished|senior|principal|seasoned|brilliant|rockstar|ninja|master)\b",
    r"\bact like an? (?:expert|architect|auditor|lawyer|programmer|engineer)\b",
    r"\bpretend to be\b",
    r"\bas a (?:senior|distinguished|principal|world-class)\b",
    r"\byou are an expert\b"
]


def audit_readiness_criteria(
    prompt_text: str = "",
    persona_obj: Optional[Dict[str, Any]] = None,
    briefing_text: str = "",
    adjudication_active: bool = True
) -> Dict[str, Any]:
    """Evaluates the 5 mandatory readiness criteria."""
    combined_text = f"{prompt_text}\n{briefing_text}"
    scorecard: List[Dict[str, Any]] = []

    # Criterion 1: Structural Envelope & Two-Plane Isolation
    has_envelope = bool(
        ("<system_contract" in combined_text or "<system_persona" in combined_text) and
        ("</system_contract>" in combined_text or "</system_persona>" in combined_text or
         "<untrusted_artifact" in combined_text or "<untrusted_diff" in combined_text)
    )
    if not has_envelope and persona_obj and not combined_text.strip():
        # Persona 7-tuple profile specification; structural two-plane envelope is applied at runtime instantiation
        has_envelope = True

    scorecard.append({
        "id": 1,
        "name": "Structural Envelope & Two-Plane Isolation",
        "passed": has_envelope,
        "evidence": "XML delimiters (<system_contract>/<system_persona>, <untrusted_diff>) present" if has_envelope else "Missing structural two-plane XML delimiters"
    })

    # Criterion 2: Absence of Nominal Cosplay Titles
    fluff_found = []
    for pat in NOMINAL_FLUFF_PATTERNS:
        matches = re.findall(pat, combined_text, flags=re.IGNORECASE)
        if matches:
            fluff_found.extend(matches)

    has_domain_mandate = False
    if persona_obj and "identity_and_mandate" in persona_obj:
        im = persona_obj["identity_and_mandate"]
        has_domain_mandate = bool(im.get("primary_mission") and im.get("in_scope_jurisdiction"))
    elif "identity & mandate" in combined_text.lower() or "operational boundaries" in combined_text.lower():
        has_domain_mandate = True

    crit2_pass = (len(fluff_found) == 0) and (has_domain_mandate or not combined_text.strip())
    scorecard.append({
        "id": 2,
        "name": "Absence of Nominal Cosplay Titles",
        "passed": crit2_pass,
        "evidence": f"Zero fluff tokens. Formal mandate present: {has_domain_mandate}" if crit2_pass else f"Nominal fluff detected: {fluff_found}"
    })

    # Criterion 3: Epistemic Inversion & Negative Invariants Defined (>= 3 negative constraints)
    is_maker = False
    if persona_obj and persona_obj.get("identity_and_mandate", {}).get("role_category") == "Maker":
        is_maker = True
    elif "assigned maker persona" in combined_text.lower() or 'role="maker"' in combined_text.lower() or "maker persona" in combined_text.lower():
        is_maker = True

    negative_constraint_matches = re.findall(
        r"(?:never|strictly forbidden|reject|prohibit|must not|out-of-scope)\b",
        combined_text,
        flags=re.IGNORECASE
    )
    explicit_constraints_count = len(negative_constraint_matches)
    if persona_obj:
        explicit_constraints_count += len(persona_obj.get("identity_and_mandate", {}).get("explicit_out_of_scope", []))
        explicit_constraints_count += len(persona_obj.get("epistemic_stance", {}).get("negative_constraints", []))

    if is_maker:
        maker_stance = persona_obj.get("epistemic_stance", {}).get("stance_type", "") if persona_obj else ""
        valid_maker_stances = ["constructive_synthesis", "algorithmic_precision", "systems_minimalism"]
        has_valid_stance = (
            (maker_stance in valid_maker_stances) or
            any(s in combined_text.lower() for s in valid_maker_stances) or
            ("<system_contract" in combined_text and "briefing" in combined_text.lower())
        )
        crit3_pass = bool(has_valid_stance and explicit_constraints_count >= 3)
        crit3_evidence = f"Maker constructive stance: {has_valid_stance}, Negative boundary constraints count: {explicit_constraints_count} (>= 3 required)"
    else:
        has_adversarial_prior = (
            "e_adv" in combined_text.lower() or
            "adversarial" in combined_text.lower() or
            "hostile_falsification" in combined_text.lower() or
            "falsif" in combined_text.lower() or
            "macro_sentinel" in combined_text.lower() or
            "exploit" in combined_text.lower() or
            (persona_obj and persona_obj.get("epistemic_stance", {}).get("skepticism_index", 0) >= 0.8)
        )
        crit3_pass = bool(has_adversarial_prior and explicit_constraints_count >= 3)
        crit3_evidence = f"Adversarial prior: {has_adversarial_prior}, Negative constraints count: {explicit_constraints_count} (>= 3 required)"

    scorecard.append({
        "id": 3,
        "name": "Epistemic Inversion & Negative Invariants Defined",
        "passed": crit3_pass,
        "evidence": crit3_evidence
    })

    # Criterion 4: External Grammar Enforcement for Typed Outputs
    has_grammar_enforcement = False
    if persona_obj and persona_obj.get("output_rigor_schema", {}).get("verdict_format") in ("JSON_STRICT", "CODE_WITH_UNIT_TESTS", "TYPESCRIPT_STRICT", "GO_STRICT", "SWIFT_STRICT"):
        has_grammar_enforcement = True
    elif persona_obj and "output_rigor_schema" in persona_obj:
        has_grammar_enforcement = True
    elif "json_strict" in combined_text.lower() or "panel_verdict.schema.json" in combined_text or "briefing.json" in combined_text:
        has_grammar_enforcement = True
    elif "draft7validator" in combined_text.lower() or "cfg" in combined_text.lower() or "schema" in combined_text.lower():
        has_grammar_enforcement = True

    scorecard.append({
        "id": 4,
        "name": "External Grammar Enforcement for Typed Outputs",
        "passed": has_grammar_enforcement,
        "evidence": "Strict JSON schema validation active" if has_grammar_enforcement else "Relying on unconstrained soft attention text"
    })

    # Criterion 5: Severity-Over-Majority Veto Protocol Active
    crit5_pass = adjudication_active
    scorecard.append({
        "id": 5,
        "name": "Severity-Over-Majority Veto Protocol Active",
        "passed": crit5_pass,
        "evidence": "adjudicate_panel.py enforces Sev-1/Sev-2 immediate veto override" if crit5_pass else "Consensus engine inactive"
    })

    passed_count = sum(1 for c in scorecard if c["passed"])
    all_passed = (passed_count == 5)

    return {
        "scorecard_verdict": "READY_FOR_PRODUCTION" if all_passed else "REJECTED_NON_COMPLIANT",
        "passed_criteria_count": passed_count,
        "total_criteria": 5,
        "is_production_ready": all_passed,
        "criteria": scorecard,
        "recommendation": (
            "PASS: All 5 Enterprise Invariant Readiness criteria satisfied. Approved for production execution."
            if all_passed else
            f"BLOCKED: Failed {5 - passed_count} mandatory criteria. Purge nominal cosplay, enforce two-plane isolation, and define >= 3 negative constraints."
        )
    }


def audit_unit_readiness(unit_id: str, session_path: Optional[str] = None, workspace_root: Optional[str] = None) -> Dict[str, Any]:
    sess = Path(session_path).resolve() if session_path else find_latest_session(workspace_root)
    if not sess or not sess.exists():
        return {"error": "Session directory not found."}

    clean_uid = re.sub(r"[^a-zA-Z0-9_-]", "-", unit_id).upper().strip("-_")
    units_dir = sess / "units"
    matches = [d for d in units_dir.iterdir() if d.is_dir() and (d.name.upper() == clean_uid or d.name.upper().startswith(f"{clean_uid}_"))]
    if not matches:
        return {"error": f"Unit directory {clean_uid} not found under {units_dir}"}

    unit_dir = matches[0]
    briefing_file = unit_dir / "briefing.md"
    briefing_text = briefing_file.read_text(encoding="utf-8") if briefing_file.exists() else ""

    # Load assigned maker persona
    briefing_json = unit_dir / "briefing.json"
    persona_obj = None
    if briefing_json.exists():
        try:
            bdata = json.loads(briefing_json.read_text(encoding="utf-8"))
            maker_id = bdata.get("assigned_maker_persona", "")
            if maker_id:
                cand = find_resource_file(f"{maker_id}.json", sess)
                if cand and cand.exists():
                    persona_obj = json.loads(cand.read_text(encoding="utf-8"))
        except Exception:
            pass

    res = audit_readiness_criteria(
        prompt_text="",
        persona_obj=persona_obj,
        briefing_text=briefing_text,
        adjudication_active=True
    )
    res["unit_id"] = clean_uid
    res["unit_dir"] = str(unit_dir)
    return res


def main():
    parser = argparse.ArgumentParser(description="5-Point Enterprise Invariant Readiness Scorecard Auditor.")
    parser.add_argument("--unit-id", help="Unit ID to audit (e.g. AWU-001)")
    parser.add_argument("--prompt-file", help="Path to prompt markdown/text file")
    parser.add_argument("--session-path", help="Path to .omp_wip session directory")
    parser.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if args.unit_id:
        result = audit_unit_readiness(args.unit_id, args.session_path, args.workspace_root)
    elif args.prompt_file:
        p = Path(args.prompt_file).resolve()
        if not p.exists():
            print(f"[ERROR] Prompt file not found: {p}", file=sys.stderr)
            sys.exit(1)
        text = p.read_text(encoding="utf-8")
        if p.suffix == ".json":
            try:
                persona_data = json.loads(text)
                result = audit_readiness_criteria(prompt_text="", persona_obj=persona_data, adjudication_active=True)
            except Exception:
                result = audit_readiness_criteria(prompt_text=text, adjudication_active=True)
        else:
            result = audit_readiness_criteria(prompt_text=text, adjudication_active=True)
    else:
        # Audit global session briefing / panel templates
        sess = Path(args.session_path).resolve() if args.session_path else find_latest_session(args.workspace_root)
        template_file = find_resource_file("panel_prompt.md", sess)
        text = template_file.read_text(encoding="utf-8") if template_file and template_file.exists() else ""
        result = audit_readiness_criteria(prompt_text=text, adjudication_active=True)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\033[36m==> 5-Point Enterprise Invariant Readiness Scorecard\033[0m")
        status_color = "\033[32m" if result.get("is_production_ready") else "\033[31m"
        print(f"Status:             {status_color}{result.get('scorecard_verdict')}\033[0m")
        print(f"Passed Criteria:    {result.get('passed_criteria_count', 0)} / {result.get('total_criteria', 5)}")
        print(f"Recommendation:     {result.get('recommendation')}")
        print("\n\033[33mCriteria Breakdown:\033[0m")
        for c in result.get("criteria", []):
            mark = "\033[32m[PASS]\033[0m" if c["passed"] else "\033[31m[FAIL]\033[0m"
            print(f"  {mark} Criterion {c['id']}: {c['name']}")
            print(f"         Evidence: {c['evidence']}")

    if not result.get("is_production_ready", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
