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
  fdag iga-check   - Audit specifications for latent Input Gaps & Plausibility Trap
  fdag test        - Run the exhaustive end-to-end regression test suite
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


ENGINE_DIR = Path(__file__).parent.resolve()


def cmd_init(args):
    from scaffold_dag_unit import find_latest_session
    import datetime, json

    moniker = args.task_moniker or "fdag-session"
    ws = Path(args.workspace_root).resolve() if args.workspace_root else Path.cwd().resolve()
    wip_dir = ws / ".omp_wip"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sess_name = f"{now_str}_{moniker}"
    sess_dir = wip_dir / sess_name

    for sub in ["00_cartography", "01_dag", "01_dag/bga_proposals", "units", "99_final_review"]:
        (sess_dir / sub).mkdir(parents=True, exist_ok=True)

    manifest_v2 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "session_id": sess_name,
        "task_moniker": moniker,
        "graph_version": 2,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "nodes": []
    }
    (sess_dir / "01_dag" / "dag_manifest.json").write_text(json.dumps(manifest_v2, indent=2), encoding="utf-8")
    print(f"\033[36m==> F-DAG Session Initialized:\033[0m {sess_dir}")


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
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json
    )


def cmd_falsify(args):
    from smt_contract_verifier import demo_falsification_suite
    demo_falsification_suite()


def cmd_frame_check(args):
    from frame_condition_auditor import audit_unit_frame_conditions
    audit_unit_frame_conditions(
        unit_id=args.unit_id,
        manifest_path=args.manifest_path,
        modified_files=args.files,
        workspace_root=args.workspace_root,
        json_output=args.json
    )


def cmd_adjudicate(args):
    from adjudicate_panel import formal_adjudicate_unit
    formal_adjudicate_unit(
        unit_id=args.unit_id,
        session_path=args.session_path,
        workspace_root=args.workspace_root,
        json_output=args.json
    )


def cmd_scorecard(args):
    from audit_readiness_scorecard import audit_unit_readiness, audit_readiness_criteria
    import json
    if args.unit_id:
        res = audit_unit_readiness(args.unit_id, args.session_path, args.workspace_root)
    elif args.prompt_file:
        p = Path(args.prompt_file).resolve()
        res = audit_readiness_criteria(prompt_text=p.read_text(encoding="utf-8"), adjudication_active=True)
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


def main():
    parser = argparse.ArgumentParser(
        prog="fdag",
        description="F-DAG: Formal-Agentic DAG Engine CLI Toolchain"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new F-DAG session")
    p_init.add_argument("--task-moniker", required=True, help="Moniker for session")
    p_init.add_argument("--workspace-root", help="Root directory")
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
    p_adj.add_argument("--json", action="store_true", help="Emit JSON")
    p_adj.set_defaults(func=cmd_adjudicate)

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

    # test
    p_test = subparsers.add_parser("test", help="Run comprehensive test suite")
    p_test.add_argument("-v", "--verbose", action="store_true", help="Verbose test runner output")
    p_test.set_defaults(func=cmd_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
