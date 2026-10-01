#!/usr/bin/env python3
"""
fdag.py - Unified Command-Line Interface for the Formal-Agentic DAG Engine (F-DAG).

Commands:
  fdag init        - Initialize a new F-DAG session with V2 manifest
  fdag validate    - Prove DAG acyclicity, critical path depth, & Bernstein concurrency
  fdag scaffold    - Scaffold an Atomic Work Unit with V2 contracts & 3-checker templates
  fdag falsify     - Execute SMT (Z3), Hypothesis (PBT), or Native boundary falsification
  fdag frame-check - Audit git diff / file writes against declared modifies frame sets
  fdag adjudicate  - Adjudicate panel verdicts with Severity-Over-Majority and waivers
  fdag scorecard   - Audit 5-Point Enterprise Invariant Readiness Scorecard
  fdag iga-check             - Audit specifications for latent Input Gaps & Plausibility Trap
  fdag clarify               - Conduct Phase 1.5 Layered Socratic Input Clarification Gate
  fdag invalidate-assumption - Register dynamic discovery assumption invalidation (Human Gate)
  fdag resolve-invalidation  - Resolve assumption invalidation Human Gate and unblock unit
  fdag test                  - Run the exhaustive end-to-end regression test suite
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ENGINE_DIR = Path(__file__).parent.resolve()


def cmd_init(args):
    from init_dag_session import init_dag_session
    init_dag_session(
        task_moniker=args.task_moniker or "fdag-session",
        workspace_root=args.workspace_root or None,
        json_output=getattr(args, "json", False),
        task_description=getattr(args, "task_description", "") or "",
        spec_file=getattr(args, "spec_file", "") or ""
    )
def cmd_validate(args):
    from validate_dag import validate_formal_dag
    ok = validate_formal_dag(
        manifest_path=args.manifest_path,
        workspace_root=args.workspace_root,
        audit_disk=args.audit_disk,
        check_concurrency=not args.no_concurrency,
        json_output=args.json
    )
    if not ok:
        sys.exit(1)


def cmd_scaffold(args):
    from scaffold_dag_unit import formal_scaffold_unit
    formal_scaffold_unit(
        unit_id=args.unit_id,
        slug=args.slug,
        title=args.title,
        maker_persona=args.maker_persona,
        checker_personas=getattr(args, "checker_personas", None),
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json
    )

def cmd_falsify(args):
    from smt_contract_verifier import demo_falsification_suite
    demo_falsification_suite()


def cmd_frame_check(args):
    from frame_condition_auditor import audit_unit_frame_conditions
    res = audit_unit_frame_conditions(
        unit_id=args.unit_id,
        manifest_path=args.manifest_path,
        modified_files=args.files,
        workspace_root=args.workspace_root,
        json_output=args.json
    )
    if not res.get("is_compliant"):
        sys.exit(1)


def cmd_adjudicate(args):
    from adjudicate_panel import formal_adjudicate_unit
    res = formal_adjudicate_unit(
        unit_id=args.unit_id,
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json,
        enforce_telemetry=getattr(args, "enforce_telemetry", False)
    )
    if "PASS" not in res.get("final_verdict", ""):
        sys.exit(1)

def cmd_scorecard(args):
    from audit_readiness_scorecard import audit_unit_readiness, audit_readiness_criteria
    import json
    if args.unit_id:
        res = audit_unit_readiness(args.unit_id, args.session_path, args.workspace_root)
    elif args.prompt_file:
        p = Path(args.prompt_file).resolve()
        if not p.exists():
            print(f"[ERROR] Prompt file not found: {p}", file=sys.stderr)
            sys.exit(1)
        text = p.read_text(encoding="utf-8")
        if p.suffix == ".json":
            try:
                persona_data = json.loads(text)
                res = audit_readiness_criteria(prompt_text="", persona_obj=persona_data, adjudication_active=True)
            except Exception:
                res = audit_readiness_criteria(prompt_text=text, adjudication_active=True)
        else:
            res = audit_readiness_criteria(prompt_text=text, adjudication_active=True)
    else:
        from dag_utils import find_latest_session, find_resource_file
        sess = Path(args.session_path).resolve() if args.session_path else find_latest_session(args.workspace_root)
        tf = find_resource_file("panel_prompt.md", sess)
        text = tf.read_text(encoding="utf-8") if tf and tf.exists() else ""
        res = audit_readiness_criteria(prompt_text=text, adjudication_active=True)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("\033[36m==> 5-Point Enterprise Invariant Readiness Scorecard\033[0m")
        status_color = "\033[32m" if res.get("is_production_ready") else "\033[31m"
        print(f"Status:             {status_color}{res.get('scorecard_verdict')}\033[0m")
        print(f"Passed Criteria:    {res.get('passed_criteria_count', 0)} / {res.get('total_criteria', 5)}")
        print(f"Recommendation:     {res.get('recommendation')}")
        print("\n\033[33mCriteria Breakdown:\033[0m")
        for c in res.get("criteria", []):
            mark = "\033[32m[PASS]\033[0m" if c["passed"] else "\033[31m[FAIL]\033[0m"
            print(f"  {mark} Criterion {c['id']}: {c['name']}")
            print(f"         Evidence: {c['evidence']}")

    if not res.get("is_production_ready", False):
        sys.exit(1)


def cmd_iga_check(args):
    from input_gap_auditor import audit_specification_text, audit_session_cartography
    import json
    if args.spec_file:
        p = Path(args.spec_file).resolve()
        if not p.exists():
            print(f"[ERROR] Specification file not found: {p}", file=sys.stderr)
            sys.exit(1)
        res = audit_specification_text(p.read_text(encoding="utf-8"))
    elif args.text:
        res = audit_specification_text(args.text)
    else:
        sess_dir = Path(args.session_path).resolve() if args.session_path else None
        res = audit_session_cartography(sess_dir, args.workspace_root)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("\033[36m==> Input Gap Analysis & Plausibility Trap Audit\033[0m")
        status_color = "\033[31m" if res.get("is_blocking") else "\033[32m"
        print(f"Verdict:              {status_color}{res.get('verdict')}\033[0m")
        print(f"Blocking Sev-1 Gaps:  {res.get('sev_1_count', 0)}")
        print(f"Ambiguous Sev-2 Gaps: {res.get('sev_2_count', 0)}")
        print(f"Authoritative Citations: {'YES' if res.get('has_authoritative_citations') else 'NO'}")
        print(f"Explanation:          {res.get('explanation')}")
        gaps = res.get("detected_gaps", [])
        if gaps:
            print("\n\033[33mIdentified Input Gaps:\033[0m")
            for idx, g in enumerate(gaps, 1):
                sev_color = "\033[31m" if g["severity"] == "Sev-1" else "\033[33m"
                print(f"  {idx}. [{sev_color}{g['severity']}\033[0m] {g['name']} ({g['category']})")
                print(f"     Description: {g['description']}")

    if res.get("is_blocking"):
        sys.exit(1)


def cmd_test(args):
    suite_path = ENGINE_DIR / "test_fdag_suite.py"
    cmd = [sys.executable, str(suite_path)]
    if args.verbose:
        cmd.append("-v")
    res = subprocess.run(cmd)
    sys.exit(res.returncode)



def cmd_panel(args):
    script = Path(__file__).parent / "dispatch_panel.py"
    cmd = [sys.executable, str(script), "--unit-id", args.unit_id]
    if getattr(args, "checker_personas", None):
        cmd.extend(["--checker-personas", args.checker_personas])
    if args.session_path:
        cmd.extend(["--session-path", args.session_path])
    if getattr(args, "dry_run", False):
        cmd.append("--dry-run")
    if getattr(args, "json", False):
        cmd.append("--json")
    res = subprocess.run(cmd)
    sys.exit(res.returncode)
def cmd_clarify(args):
    from socratic_dialogue import (
        audit_layered_input_clarification,
        step_socratic_dialogue,
        resolve_socratic_dialogue,
        format_socratic_for_ask,
        add_socratic_dialogue,
    )
    import json
    sess_dir = Path(args.session_path).resolve() if args.session_path else None

    if getattr(args, "add", False):
        if not getattr(args, "question", None):
            print("[ERROR] --question <question> is required with --add", file=sys.stderr)
            sys.exit(1)
        options = None
        if getattr(args, "options_json", None):
            try:
                options = json.loads(args.options_json)
            except Exception as e:
                print(f"[ERROR] Failed to parse --options-json: {e}", file=sys.stderr)
                sys.exit(1)
        res = add_socratic_dialogue(
            question=args.question,
            context=getattr(args, "context", "") or "",
            layer=getattr(args, "layer", "Layer 3: Socratic Intent & Trade-off Clarification") or "Layer 3: Socratic Intent & Trade-off Clarification",
            recommended_label=getattr(args, "recommended_label", "Enforce verified engineering standard") or "Enforce verified engineering standard",
            recommended_explanation=getattr(args, "recommended_explanation", "") or "",
            recommended_tradeoff=getattr(args, "recommended_tradeoff", "") or "",
            alt_label=getattr(args, "alt_label", "Use lenient fallback defaults") or "Use lenient fallback defaults",
            alt_explanation=getattr(args, "alt_explanation", "") or "",
            alt_tradeoff=getattr(args, "alt_tradeoff", "") or "",
            options=options,
            session_dir=sess_dir,
            workspace_root=args.workspace_root
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("success"):
                print(f"\033[32m✓ Registered Socratic dialogue {res.get('dialogue_id')}.\033[0m")
                print(f"Target Question: {args.question}")
                print(f"Total Questions in Series: {res.get('total_questions')}")
                print(f"Run 'fdag clarify --step' to review or 'fdag clarify --step --ask-format' for OMP ask tool.")
            else:
                print(f"\033[31m[ERROR] Failed to add Socratic dialogue: {res.get('error')}\033[0m", file=sys.stderr)
                sys.exit(1)
        return

    if args.step:
        res = step_socratic_dialogue(session_dir=sess_dir, workspace_root=args.workspace_root)
        if not res:
            if args.json:
                print(json.dumps({"has_pending": False, "status": "RESOLVED"}))
            else:
                print("\033[32m✓ All Socratic dialogue inquiries resolved! Gate passed.\033[0m")
            return
        if getattr(args, "ask_format", False):
            ask_payload = format_socratic_for_ask(res)
            print(json.dumps({"questions": [ask_payload]}, indent=2))
            return
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"\033[36m==> Socratic Dialogue {res.get('dialogue_id')} (Question {res.get('question_index')} of {res.get('total_in_series')})\033[0m")
            print(f"\033[33mContext & Observable Reality:\033[0m\n{res.get('context_and_reality')}\n")
            print(f"\033[1mTarget Question:\033[0m {res.get('question')}\n")
            print("\033[33mEvaluated Options:\033[0m")
            for opt in res.get("options", []):
                rec = " \033[32m(Recommended)\033[0m" if opt.get("is_recommended") else ""
                clean_lbl = re.sub(r"^\(Recommended\)\s*", "", opt.get("label", ""))
                print(f"  • [{opt.get('id')}]{rec} {clean_lbl}")
                print(f"    Explanation: {opt.get('plain_language_explanation')}")
                print(f"    Trade-off:   {opt.get('trade_off_analysis')}\n")
        return

    if args.resolve:
        if not args.option:
            print("[ERROR] --option <option_id> is required with --resolve", file=sys.stderr)
            sys.exit(1)
        res = resolve_socratic_dialogue(
            dialogue_id=args.resolve,
            selected_option_id=args.option,
            custom_input=args.custom,
            session_dir=sess_dir,
            workspace_root=args.workspace_root
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("success"):
                print(f"\033[32m✓ Socratic dialogue {args.resolve} resolved with option {args.option}.\033[0m")
                if res.get("is_all_resolved"):
                    print("\033[32m✓ All input clarification questions resolved! Gate passed.\033[0m")
                else:
                    print(f"Next active question: {res.get('next_dialogue_id')}")
            else:
                print(f"\033[31m[ERROR] Failed to resolve dialogue: {res.get('error')}\033[0m", file=sys.stderr)
                sys.exit(1)
        return

    # Default: run audit
    spec_text = None
    if args.spec_file:
        sp = Path(args.spec_file).resolve()
        if not sp.exists():
            print(f"[ERROR] Specification file not found: {sp}", file=sys.stderr)
            sys.exit(1)
        spec_text = sp.read_text(encoding="utf-8")
    res = audit_layered_input_clarification(session_dir=sess_dir, workspace_root=args.workspace_root, spec_text=spec_text)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        status_color = "\033[31m" if res.get("is_blocking") else "\033[32m"
        print(f"\033[36m==> Phase 1.5 Layered Socratic Input Clarification Gate\033[0m")
        print(f"Status:             {status_color}{res.get('status')}\033[0m")
        print(f"Total Questions:    {res.get('total_questions', 0)}")
        print(f"Pending Questions:  {res.get('pending_questions', 0)}")
        print(f"Explanation:        {res.get('explanation')}")
        if res.get("is_blocking"):
            next_q = step_socratic_dialogue(session_dir=sess_dir, workspace_root=args.workspace_root)
            if next_q:
                print("\n" + "=" * 68)
                print(f"\033[36m==> Active Socratic Inquiry: {next_q.get('dialogue_id')} (Question {next_q.get('question_index')} of {next_q.get('total_in_series')})\033[0m")
                print(f"\033[33mContext & Observable Reality:\033[0m\n{next_q.get('context_and_reality')}\n")
                print(f"\033[1mTarget Question:\033[0m {next_q.get('question')}\n")
                print("\033[33mEvaluated Options:\033[0m")
                for opt in next_q.get("options", []):
                    rec = " \033[32m(Recommended)\033[0m" if opt.get("is_recommended") else ""
                    clean_lbl = re.sub(r"^\(Recommended\)\s*", "", opt.get("label", ""))
                    print(f"  • [{opt.get('id')}]{rec} {clean_lbl}")
                    print(f"    Explanation: {opt.get('plain_language_explanation')}")
                    print(f"    Trade-off:   {opt.get('trade_off_analysis')}\n")
                print(f"To resolve, run:\n  fdag clarify --resolve {next_q.get('dialogue_id')} --option <OPTION_ID>")
                print("=" * 68 + "\n")
            sys.exit(1)


def cmd_invalidate_assumption(args):
    from socratic_dialogue import register_assumption_invalidation
    import json
    sess_dir = Path(args.session_path).resolve() if args.session_path else None
    res = register_assumption_invalidation(
        unit_id=args.unit_id,
        assumption_summary=args.assumption,
        discovery_evidence=args.evidence,
        session_dir=sess_dir,
        workspace_root=args.workspace_root
    )
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if res.get("success"):
            print(f"\033[31m==> MANDATORY HUMAN GATE TRIGGERED: {res.get('invalidation_id')}\033[0m")
            print(f"Unit {args.unit_id} placed in BLOCKED status.")
            print(f"Invalidated Assumption: {args.assumption}")
            print(f"Empirical Discovery:    {args.evidence}")
            print(f"\033[33mSocratic dialogue queued. Human decision required before resuming execution.\033[0m")
        else:
            print(f"[ERROR] {res.get('error')}", file=sys.stderr)
            sys.exit(1)


def cmd_resolve_invalidation(args):
    from socratic_dialogue import resolve_assumption_invalidation
    import json
    sess_dir = Path(args.session_path).resolve() if args.session_path else None
    res = resolve_assumption_invalidation(
        invalidation_id=args.invalidation_id,
        selected_option_id=args.option_id,
        resolution_summary=args.summary,
        session_dir=sess_dir,
        workspace_root=args.workspace_root
    )
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if res.get("success"):
            print(f"\033[32m✓ Invalidation gate {args.invalidation_id} resolved!\033[0m")
            print(f"Unit {res.get('unit_id')} has been unblocked and restored to IN_PROGRESS.")
            print(f"Resolution summary: {args.summary}")
        else:
            print(f"[ERROR] {res.get('error')}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        prog="fdag",
        description="F-DAG: Formal-Agentic DAG Engine CLI Toolchain"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new F-DAG session")
    p_init.add_argument("--task-moniker", required=True, help="Moniker for session")
    p_init.add_argument("-d", "--task-description", "--task-desc", "--spec-text", default="", help="Verbatim user request or task specification")
    p_init.add_argument("-s", "--spec-file", default="", help="Path to raw specification text file")
    p_init.add_argument("--workspace-root", help="Root directory")
    p_init.add_argument("--json", action="store_true", help="Emit JSON output")
    p_init.set_defaults(func=cmd_init)
    # validate
    p_val = subparsers.add_parser("validate", help="Validate DAG manifest, cycle, and Bernstein concurrency")
    p_val.add_argument("--manifest-path", help="Path to dag_manifest.json")
    p_val.add_argument("--workspace-root", help="Workspace root")
    p_val.add_argument("--audit-disk", action="store_true", help="Audit on-disk contracts")
    p_val.add_argument("--no-concurrency", action="store_true", help="Skip concurrency check")
    p_val.add_argument("--json", action="store_true", help="Emit JSON output")
    p_val.set_defaults(func=cmd_validate)

    # scaffold
    p_scaf = subparsers.add_parser("scaffold", help="Scaffold an Atomic Work Unit")
    p_scaf.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    p_scaf.add_argument("--slug", help="URL-safe slug")
    p_scaf.add_argument("--title", help="Unit title")
    p_scaf.add_argument("--maker-persona", help="Maker persona ID")
    p_scaf.add_argument("--checker-personas", help="Checker persona IDs (comma-separated or JSON list)")
    p_scaf.add_argument("--session-path", help="Session directory")
    p_scaf.add_argument("--workspace-root", help="Workspace root")
    p_scaf.add_argument("--json", action="store_true", help="Emit JSON output")
    p_scaf.set_defaults(func=cmd_scaffold)

    # falsify
    p_fal = subparsers.add_parser("falsify", help="Execute contract falsification (Z3 / Hypothesis / Native)")
    p_fal.add_argument("--demo", action="store_true", default=True, help="Run demonstration falsification suite")
    p_fal.set_defaults(func=cmd_falsify)

    # frame-check
    p_fc = subparsers.add_parser("frame-check", help="Audit frame conditions against git diff")
    p_fc.add_argument("--unit-id", required=True, help="Unit ID")
    p_fc.add_argument("--manifest-path", required=True, help="Path to manifest")
    p_fc.add_argument("--files", nargs="*", help="Files to audit")
    p_fc.add_argument("--workspace-root", help="Workspace root")
    p_fc.add_argument("--json", action="store_true", help="Emit JSON")
    p_fc.set_defaults(func=cmd_frame_check)

    # adjudicate
    p_adj = subparsers.add_parser("adjudicate", help="Adjudicate 3-agent panel with Severity-Over-Majority")
    p_adj.add_argument("--unit-id", required=True, help="Unit ID")
    p_adj.add_argument("--session-path", help="Session directory")
    p_adj.add_argument("--workspace-root", help="Workspace root")
    p_adj.add_argument("--enforce-telemetry", action="store_true", help="Strictly require subagent telemetry attestation")
    p_adj.add_argument("--json", action="store_true", help="Emit JSON")
    p_adj.set_defaults(func=cmd_adjudicate)
    # panel
    p_pan = subparsers.add_parser("panel", help="Dispatch multi-model adversarial verification panel via subagents")
    p_pan.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    p_pan.add_argument("--checker-personas", help="Override checker persona IDs (comma-separated or JSON list)")
    p_pan.add_argument("--session-path", help="Session directory")
    p_pan.add_argument("--dry-run", action="store_true", help="Dry-run: generate task payload without dispatch")
    p_pan.add_argument("--json", action="store_true", help="Emit JSON")
    p_pan.set_defaults(func=cmd_panel)

    # scorecard
    p_sc = subparsers.add_parser("scorecard", help="Audit 5-Point Enterprise Invariant Readiness Scorecard")
    p_sc.add_argument("--unit-id", help="Unit ID to audit")
    p_sc.add_argument("--prompt-file", help="Path to prompt markdown file")
    p_sc.add_argument("--session-path", help="Session directory")
    p_sc.add_argument("--workspace-root", help="Workspace root")
    p_sc.add_argument("--json", action="store_true", help="Emit JSON output")
    p_sc.set_defaults(func=cmd_scorecard)

    # iga-check
    p_iga = subparsers.add_parser("iga-check", help="Audit specifications for latent Input Gaps (Plausibility Trap)")
    p_iga.add_argument("--spec-file", help="Path to specification file")
    p_iga.add_argument("--text", help="Raw specification text")
    p_iga.add_argument("--session-path", help="Session directory")
    p_iga.add_argument("--workspace-root", help="Workspace root")
    p_iga.add_argument("--json", action="store_true", help="Emit JSON output")
    p_iga.set_defaults(func=cmd_iga_check)

    # clarify
    p_clar = subparsers.add_parser("clarify", help="Audit or conduct Phase 1.5 Socratic Input Clarification")
    p_clar.add_argument("--spec-file", help="Path to specification file")
    p_clar.add_argument("--session-path", help="Session directory")
    p_clar.add_argument("--workspace-root", help="Workspace root")
    p_clar.add_argument("--step", action="store_true", help="Display next pending Socratic dialogue inquiry")
    p_clar.add_argument("--ask-format", action="store_true", help="Format output for direct OMP ask tool invocation")
    p_clar.add_argument("--resolve", help="Dialogue ID to resolve (e.g. SOCRATIC-001)")
    p_clar.add_argument("--option", help="Option ID selected by human (e.g. OPT-1)")
    p_clar.add_argument("--custom", help="Custom user clarification or rationale")
    p_clar.add_argument("--add", action="store_true", help="Register a new Socratic dialogue question (Human Gate)")
    p_clar.add_argument("--question", help="Target question (must end with ?)")
    p_clar.add_argument("--context", default="", help="Context and observable reality")
    p_clar.add_argument("--layer", default="Layer 3: Socratic Intent & Trade-off Clarification", help="Clarification layer")
    p_clar.add_argument("--recommended-label", default="Enforce verified engineering standard", help="Option 1 (Recommended) label")
    p_clar.add_argument("--recommended-explanation", default="", help="Option 1 plain language explanation")
    p_clar.add_argument("--recommended-tradeoff", default="", help="Option 1 trade-off analysis")
    p_clar.add_argument("--alt-label", default="Use lenient fallback defaults", help="Option 2 alternative label")
    p_clar.add_argument("--alt-explanation", default="", help="Option 2 plain language explanation")
    p_clar.add_argument("--alt-tradeoff", default="", help="Option 2 trade-off analysis")
    p_clar.add_argument("--options-json", default="", help="JSON string for custom options array")
    p_clar.add_argument("--json", action="store_true", help="Emit JSON output")
    p_clar.set_defaults(func=cmd_clarify)

    # invalidate-assumption
    p_inval = subparsers.add_parser("invalidate-assumption", help="Register dynamic discovery assumption invalidation (Human Gate)")
    p_inval.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    p_inval.add_argument("--assumption", required=True, help="Invalidated prior assumption")
    p_inval.add_argument("--evidence", required=True, help="Empirical discovery evidence or error trace")
    p_inval.add_argument("--session-path", help="Session directory")
    p_inval.add_argument("--workspace-root", help="Workspace root")
    p_inval.add_argument("--json", action="store_true", help="Emit JSON output")
    p_inval.set_defaults(func=cmd_invalidate_assumption)

    # resolve-invalidation
    p_res_inval = subparsers.add_parser("resolve-invalidation", help="Resolve assumption invalidation Human Gate")
    p_res_inval.add_argument("--invalidation-id", required=True, help="Invalidation ID (e.g. INVAL-001)")
    p_res_inval.add_argument("--option-id", required=True, help="Selected Option ID (e.g. OPT-1)")
    p_res_inval.add_argument("--summary", required=True, help="Human resolution summary")
    p_res_inval.add_argument("--session-path", help="Session directory")
    p_res_inval.add_argument("--workspace-root", help="Workspace root")
    p_res_inval.add_argument("--json", action="store_true", help="Emit JSON output")
    p_res_inval.set_defaults(func=cmd_resolve_invalidation)

    # test
    p_test = subparsers.add_parser("test", help="Run comprehensive test suite")
    p_test.add_argument("-v", "--verbose", action="store_true", help="Verbose test runner output")
    p_test.set_defaults(func=cmd_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
