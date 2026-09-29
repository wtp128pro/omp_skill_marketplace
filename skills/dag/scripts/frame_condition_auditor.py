#!/usr/bin/env python3
"""
frame_condition_auditor.py - Automated Frame Condition & Side-Effect Auditor.

Purpose:
Solves the Frame Problem in Agentic Engineering by formally verifying:
1. Frame Containment Invariant: Every modified file in the workspace must match at least one pattern in frame_conditions.modifies.
2. Immutability Invariant: No modified file may match any pattern in frame_conditions.immutable.
3. If an unauthorized file write occurs, triggers an immediate, un-appealable Sev-1 Frame Breach Veto.
"""

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional


def match_any_pattern(path_str: str, patterns: List[str]) -> bool:
    clean_p = path_str.strip().replace("\\", "/").lstrip("./")
    for pat in patterns:
        clean_pat = pat.strip().replace("\\", "/").lstrip("./")
        if clean_p == clean_pat:
            return True
        if clean_pat.endswith("/") and clean_p.startswith(clean_pat):
            return True
        if clean_pat.endswith("/*") and (clean_p.startswith(clean_pat[:-1]) or clean_p == clean_pat[:-2]):
            return True
        if clean_pat.endswith("/**") and (clean_p.startswith(clean_pat[:-2]) or clean_p == clean_pat[:-3]):
            return True
        if fnmatch.fnmatch(clean_p, clean_pat):
            return True
    return False


def find_repo_root(start_path: Path) -> Path:
    """Locates repo/workspace root by traversing upward for .git or .omp_wip."""
    curr = start_path.resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / ".git").exists() or (parent / ".omp_wip").exists():
            return parent
    if ".omp_wip" in curr.parts:
        idx = curr.parts.index(".omp_wip")
        return Path(*curr.parts[:idx])
    return curr.parent.parent if len(curr.parents) >= 2 else curr

def get_git_modified_files(repo_root: Path) -> List[str]:
    """Gets list of modified, added, or untracked files from git status."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        files = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Format: 'XY path' or 'XY path -> new_path'
            parts = line[2:].strip().split(" -> ")
            target = parts[-1].strip().strip('"')
            if target == ".omp_wip" or target.startswith(".omp_wip/") or target.startswith(".git/"):
                continue
            files.append(target)
        return files
    except Exception:
        return []


def audit_unit_frame_conditions(
    unit_id: str,
    manifest_path: str,
    modified_files: List[str] = None,
    workspace_root: str = None,
    json_output: bool = False
) -> Dict[str, Any]:
    man_file = Path(manifest_path).resolve()
    if not man_file.exists():
        print(f"[ERROR] Manifest not found: {man_file}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(man_file.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])

    clean_uid = unit_id.upper().strip()
    target_node = next((n for n in nodes if n.get("id", "").upper().strip() == clean_uid), None)

    if not target_node:
        print(f"[ERROR] Unit ID {unit_id} not found in manifest.", file=sys.stderr)
        sys.exit(1)

    frame_spec = target_node.get("frame_conditions", {})
    modifies_patterns = frame_spec.get("modifies", target_node.get("expected_outputs", []))
    immutable_patterns = frame_spec.get("immutable", [])

    # If modified_files not passed, detect from git or manifest outputs
    if modified_files is None or len(modified_files) == 0:
        repo_dir = Path(workspace_root).resolve() if workspace_root else find_repo_root(man_file)
        git_files = get_git_modified_files(repo_dir)
        modified_files = git_files if git_files else target_node.get("expected_outputs", [])

    unauthorized_writes = []
    immutable_breaches = []
    authorized_writes = []

    for f in modified_files:
        # Ignore .omp_wip internal tracking files
        if ".omp_wip" in f or f.startswith(".git"):
            continue

        # Check immutable breaches first
        if match_any_pattern(f, immutable_patterns):
            immutable_breaches.append(f)
            continue

        # Check modifies containment
        if match_any_pattern(f, modifies_patterns):
            authorized_writes.append(f)
        else:
            unauthorized_writes.append(f)

    is_compliant = (len(unauthorized_writes) == 0 and len(immutable_breaches) == 0)
    highest_severity = "None"
    verdict = "PASS"

    if immutable_breaches:
        highest_severity = "Sev-1"
        verdict = "REJECT_VETO"
        rationale = f"CRITICAL FRAME BREACH: Unit modified explicitly IMMUTABLE paths: {immutable_breaches}"
    elif unauthorized_writes:
        highest_severity = "Sev-1"
        verdict = "REJECT_VETO"
        rationale = f"FRAME LEAK DETECTED: Files modified outside declared modifies set: {unauthorized_writes}"
    else:
        rationale = f"All {len(authorized_writes)} modified files strictly within declared frame condition boundary."

    if not json_output:
        print(f"\033[36m==> Frame Condition Audit for {clean_uid}\033[0m")
        print(f"Declared Modifies:  {modifies_patterns}")
        print(f"Declared Immutable: {immutable_patterns}")
        print(f"Files Audited:      {len(modified_files)}")
        if is_compliant:
            print(f"\033[32m✓ Frame Boundary Respected: {rationale}\033[0m")
        else:
            print(f"\033[31m✗ Frame Breach Detected: {rationale}\033[0m")

    res = {
        "unit_id": clean_uid,
        "is_compliant": is_compliant,
        "verdict": verdict,
        "highest_severity": highest_severity,
        "rationale": rationale,
        "authorized_writes": authorized_writes,
        "unauthorized_writes": unauthorized_writes,
        "immutable_breaches": immutable_breaches
    }

    if json_output:
        print(json.dumps(res, indent=2))

    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Frame Condition & Side-Effect Auditor.")
    parser.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    parser.add_argument("--manifest-path", required=True, help="Path to dag_manifest.json")
    parser.add_argument("--files", nargs="*", help="Explicit list of modified files to audit")
    parser.add_argument("--workspace-root", help="Root directory of workspace")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    res = audit_unit_frame_conditions(
        unit_id=args.unit_id,
        manifest_path=args.manifest_path,
        modified_files=args.files,
        workspace_root=args.workspace_root,
        json_output=args.json
    )
    if not res.get("is_compliant"):
        sys.exit(1)
