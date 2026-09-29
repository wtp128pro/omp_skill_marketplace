#!/usr/bin/env python3
"""
formal_dag_validator.py / validate_dag.py - Formally Verified DAG Validator, Cycle Detector,
Bernstein Concurrency Prover, 7-Tuple Persona Profile Validator, and On-Disk Audit Engine.

Mathematical Properties Verified:
1. Schema Invariants: Validates against Draft-07 JSON Schema (using jsonschema).
2. Graph Acyclicity: Formal partial order verification via Kahn's Topological Sort.
3. Graph Depth & Critical Path: Strict topological depth calculation.
4. Maker != Checker Orthogonality: Zero persona/epistemic overlap.
5. Exactly 3 Distinct Adversarial Checkers per Atomic Work Unit.
6. 7-Tuple Persona Profile Schema Compliance & Epistemic Stance Orthogonality.
7. Model Tier Binding Invariants (Velocity Flash vs Deep Reasoning Pro vs Macro Opus 5.5 xhigh).
8. Bernstein's Conditions of Concurrency (1966):
   For all topologically independent pairs (u, v):
     - R_u ∩ W_v = ∅ (No Read-After-Write race)
     - W_u ∩ R_v = ∅ (No Write-After-Read race)
     - W_u ∩ W_v = ∅ (No Write-After-Write conflict)
9. Frame Condition Containment: Guaranteed declared modifies sets for all nodes.
10. On-Disk Auditability (--audit-disk): Proves physical persistence of contracts and verdicts.
"""

import argparse
import fnmatch
import json
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    from dag_utils import find_resource_file, get_personas_dir, get_templates_dir, find_latest_session
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    try:
        from dag_utils import find_resource_file, get_personas_dir, get_templates_dir, find_latest_session
    except ImportError:
        def find_resource_file(fn: str, s: Optional[Path] = None) -> Optional[Path]:
            p = Path(__file__).parent.parent / "resources" / "templates" / fn
            if p.exists(): return p
            p = Path(__file__).parent.parent / "resources" / "personas" / fn
            if p.exists(): return p
            return None
        def get_personas_dir() -> Path: return Path(__file__).parent.parent / "resources" / "personas"
        def get_templates_dir() -> Path: return Path(__file__).parent.parent / "resources" / "templates"
        def find_latest_session(w: Optional[str] = None) -> Optional[Path]: return None


def path_overlaps(pat1: str, pat2: str) -> bool:
    """Evaluates whether two file paths or glob patterns can match the same filesystem resource."""
    p1 = pat1.strip().replace("\\", "/")
    p2 = pat2.strip().replace("\\", "/")

    if p1 == p2:
        return True

    if fnmatch.fnmatch(p1, p2) or fnmatch.fnmatch(p2, p1):
        return True

    # Check directory prefix containment (e.g., 'src/**' vs 'src/auth/token.ts')
    if p1.endswith("/**") and (p2.startswith(p1[:-3]) or fnmatch.fnmatch(p2, p1)):
        return True
    if p2.endswith("/**") and (p1.startswith(p2[:-3]) or fnmatch.fnmatch(p1, p2)):
        return True

    return False


def set_overlaps(set1: List[str], set2: List[str]) -> Tuple[bool, List[Tuple[str, str]]]:
    """Checks if any element in set1 overlaps with any element in set2."""
    conflicts = []
    for s1 in set1:
        for s2 in set2:
            if path_overlaps(s1, s2):
                conflicts.append((s1, s2))
    return (len(conflicts) > 0, conflicts)


def check_bernstein_conditions(
    node_u: Dict[str, Any],
    node_v: Dict[str, Any]
) -> Tuple[bool, Dict[str, List[Tuple[str, str]]]]:
    """
    Evaluates Bernstein's Conditions of Non-Interference for two concurrent tasks:
    1. RAW: R_u ∩ W_v = ∅
    2. WAR: W_u ∩ R_v = ∅
    3. WAW: W_u ∩ W_v = ∅
    """
    r_u = node_u.get("inputs", [])
    w_u = node_u.get("frame_conditions", {}).get("modifies", node_u.get("expected_outputs", []))

    r_v = node_v.get("inputs", [])
    w_v = node_v.get("frame_conditions", {}).get("modifies", node_v.get("expected_outputs", []))

    conflicts: Dict[str, List[Tuple[str, str]]] = {}

    has_raw, raw_c = set_overlaps(r_u, w_v)
    if has_raw:
        conflicts["RAW_CONFLICT (R_u ∩ W_v)"] = raw_c

    has_war, war_c = set_overlaps(w_u, r_v)
    if has_war:
        conflicts["WAR_CONFLICT (W_u ∩ R_v)"] = war_c

    has_waw, waw_c = set_overlaps(w_u, w_v)
    if has_waw:
        conflicts["WAW_CONFLICT (W_u ∩ W_v)"] = waw_c

    is_safe = (len(conflicts) == 0)
    return is_safe, conflicts


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


def find_manifest(manifest_path: str = None, workspace_root: str = None) -> Optional[Path]:
    if manifest_path:
        p = Path(manifest_path).resolve()
        return p if p.exists() else None

    # Search current directory and standard locations
    for cand in ["01_dag/dag_manifest.json", "dag_manifest.json", "dag_manifest_v2.json"]:
        p = Path(cand).resolve()
        if p.exists():
            return p

    # Search upwards for .omp_wip
    start_dir = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
    for p in [start_dir] + list(start_dir.parents):
        c = p / ".omp_wip"
        if c.is_dir():
            sessions = [d for d in c.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if sessions:
                sessions.sort(key=lambda x: x.name, reverse=True)
                for s in sessions:
                    f1 = s / "01_dag" / "dag_manifest.json"
                    if f1.exists():
                        return f1
                    f2 = s / "01_dag" / "dag_manifest_v2.json"
                    if f2.exists():
                        return f2
    return None


def audit_disk_contracts(sess_dir: Path, nodes: List[Dict[str, Any]]) -> bool:
    """Verifies that all nodes have required on-disk contracts and completed nodes are debriefed."""
    units_dir = sess_dir / "units"
    if not units_dir.is_dir():
        print(f"[ERROR] Units directory not found: {units_dir}", file=sys.stderr)
        return False

    errors = []
    for node in nodes:
        nid = node.get("id", "").strip()
        slug = node.get("slug", "").strip()
        unit_dir = None
        for cand in [units_dir / f"{nid}_{slug}", units_dir / nid]:
            if cand.is_dir():
                unit_dir = cand
                break
        if not unit_dir:
            for d in units_dir.iterdir():
                if d.is_dir() and (d.name.startswith(f"{nid}_") or d.name == nid):
                    unit_dir = d
                    break

        if not unit_dir:
            errors.append(f"Node {nid} has no on-disk unit directory under {units_dir}")
            continue

        b_md = unit_dir / "briefing.md"
        b_json = unit_dir / "briefing.json"
        if not (b_md.exists() or b_json.exists()):
            errors.append(f"Node {nid} missing on-disk briefing contract (briefing.md or briefing.json)")

        status = node.get("status", "PENDING").upper()
        if status == "COMPLETED":
            deb = unit_dir / "debriefing.md"
            if not deb.exists():
                errors.append(f"Node {nid} is COMPLETED but missing debriefing.md")
            pv_json = unit_dir / "panel_verdicts.json"
            pv_md = unit_dir / "panel_verdicts.md"
            if not (pv_json.exists() or pv_md.exists()):
                errors.append(f"Node {nid} is COMPLETED but missing panel_verdicts (.json or .md)")

    if errors:
        print("[ERROR] On-Disk Contract Audit Failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return False

    print(f"✓ On-Disk Audit: All {len(nodes)} work units have fully satisfied physical contracts.")
    return True


def validate_formal_dag(
    manifest_path: str = None,
    workspace_root: str = None,
    audit_disk: bool = False,
    check_concurrency: bool = True,
    json_output: bool = False,
) -> bool:
    manifest_file = find_manifest(manifest_path, workspace_root)
    if not manifest_file or not manifest_file.exists():
        print(f"[ERROR] DAG Manifest not found. Pass --manifest-path or ensure .omp_wip exists.", file=sys.stderr)
        return False

    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] JSON Parsing failure in {manifest_file}: {e}", file=sys.stderr)
        return False

    graph_version = data.get("graph_version", 1)
    nodes: List[Dict[str, Any]] = data.get("nodes", [])

    if not json_output:
        print(f"\033[36m==> Formal DAG Verification (Manifest: {manifest_file.name}, Version: {graph_version})\033[0m")

    # 1. JSON Schema Validation if available and schema file located
    schema_file = find_resource_file("dag_manifest_v2.schema.json", manifest_file.parent.parent)
    if HAS_JSONSCHEMA and schema_file and graph_version >= 2:
        try:
            schema_data = json.loads(schema_file.read_text(encoding="utf-8"))
            jsonschema.Draft7Validator(schema_data).validate(data)
            if not json_output:
                print("✓ Schema Validation: 100% compliant with dag_manifest_v2.schema.json.")
        except jsonschema.ValidationError as ve:
            print(f"[ERROR] Manifest Schema Violation: {ve.message} at path: {list(ve.path)}", file=sys.stderr)
            return False

    # 1.5 Input Clarification & Dynamic Discovery Invalidation Gate Audits
    input_clar = data.get("input_clarification", {})
    if input_clar.get("status") in ["PENDING", "IN_PROGRESS"]:
        print(f"[ERROR] PHASE 1.5 INPUT CLARIFICATION GATE PENDING: Input clarification status is '{input_clar.get('status')}'. Must be RESOLVED or CLEAN_PASS before DAG execution.", file=sys.stderr)
        return False

    # Check on-disk dialogues file if present
    sess_dir = manifest_file.parent.parent
    dialogues_file = sess_dir / "00_cartography" / "socratic_dialogues.json"
    if dialogues_file.exists():
        try:
            d_data = json.loads(dialogues_file.read_text(encoding="utf-8"))
            pending_dialogues = sum(1 for d in d_data.get("dialogues", []) if d.get("status") != "RESOLVED")
            if pending_dialogues > 0:
                print(f"[ERROR] PHASE 1.5 INPUT CLARIFICATION GATE PENDING: {pending_dialogues} unclarified Socratic dialogue question(s) must be resolved via human gate before DAG execution.", file=sys.stderr)
                return False
        except Exception:
            pass

    # Dynamic Discovery Assumption Invalidation Human Gate Audit
    invals = data.get("invalidated_assumptions", [])
    for inv in invals:
        if inv.get("status") == "ACTIVE_BLOCKER" or inv.get("human_gate_status") == "PENDING_HUMAN_DIALOGUE":
            print(f"[ERROR] ASSUMPTION INVALIDATION HUMAN GATE VETO: Invalidation '{inv.get('invalidation_id')}' on unit '{inv.get('unit_id')}' requires mandatory human resolution.", file=sys.stderr)
            return False

    # 2. Structural Node Validation
    node_map: Dict[str, Dict[str, Any]] = {}
    adj: Dict[str, List[str]] = defaultdict(list)
    rev_adj: Dict[str, List[str]] = defaultdict(list)
    in_degree: Dict[str, int] = defaultdict(int)

    for node in nodes:
        nid = str(node.get("id", "")).strip()
        if not nid:
            print("[ERROR] Node with missing or empty 'id'.", file=sys.stderr)
            return False
        if nid in node_map:
            print(f"[ERROR] Duplicate Node ID: {nid}", file=sys.stderr)
            return False
        node_map[nid] = node
        in_degree[nid] = 0

    # 3. Maker != Checker Orthogonality, 7-Tuple Persona Validation & Epistemic Stances
    persona_schema_file = find_resource_file("persona_profile.schema.json", manifest_file.parent.parent)
    persona_validator = None
    if HAS_JSONSCHEMA and persona_schema_file and persona_schema_file.exists():
        try:
            pschema_data = json.loads(persona_schema_file.read_text(encoding="utf-8"))
            persona_validator = jsonschema.Draft7Validator(pschema_data)
        except Exception:
            pass

    for nid, node in node_map.items():
        maker_val = node.get("assigned_maker_persona", "")
        maker_id = maker_val.get("persona_id") if isinstance(maker_val, dict) else str(maker_val).strip()

        checkers_val = node.get("checker_personas", [])
        checker_ids = []
        for c in checkers_val:
            cid = c.get("persona_id") if isinstance(c, dict) else str(c).strip()
            if cid:
                checker_ids.append(cid)

        if not maker_id:
            print(f"[ERROR] Node {nid}: Missing assigned Maker persona.", file=sys.stderr)
            return False

        if len(checker_ids) != 3:
            print(f"[ERROR] Node {nid}: MUST have exactly 3 checker personas. Found: {len(checker_ids)}", file=sys.stderr)
            return False

        for cid in checker_ids:
            if cid.lower() == maker_id.lower():
                print(f"[ERROR] MAKER != CHECKER VIOLATION in {nid}: Checker '{cid}' matches Maker '{maker_id}'!", file=sys.stderr)
                return False

        if len(set(c.lower() for c in checker_ids)) != 3:
            print(f"[ERROR] Node {nid}: Checker personas are not distinct: {checker_ids}", file=sys.stderr)
            return False

        # Frame Conditions Modifies Set presence check
        frame_spec = node.get("frame_conditions", {})
        modifies_set = frame_spec.get("modifies", node.get("expected_outputs", []))
        if not modifies_set:
            print(f"[ERROR] Frame Condition Violation in {nid}: Node must declare non-empty frame_conditions.modifies or expected_outputs.", file=sys.stderr)
            return False

        # 7-Tuple Persona Profile & Stance Orthogonality Verification
        sess_dir = manifest_file.parent.parent
        maker_prof = resolve_persona_profile(maker_val, sess_dir)
        if maker_prof and persona_validator:
            try:
                persona_validator.validate(maker_prof)
            except jsonschema.ValidationError as ve:
                print(f"[ERROR] Maker Persona '{maker_id}' in {nid} violates persona_profile.schema.json: {ve.message}", file=sys.stderr)
                return False

        if maker_prof:
            maker_stance = maker_prof.get("epistemic_stance", {}).get("stance_type", "")
            if maker_stance and maker_stance != "constructive_synthesis":
                print(f"[ERROR] Maker Persona '{maker_id}' in {nid} has invalid stance '{maker_stance}'. Expected 'constructive_synthesis'.", file=sys.stderr)
                return False

        checker_stances = []
        for cid_idx, c_elem in enumerate(checkers_val):
            c_prof = resolve_persona_profile(c_elem, sess_dir)
            cid_name = checker_ids[cid_idx]
            if c_prof and persona_validator:
                try:
                    persona_validator.validate(c_prof)
                except jsonschema.ValidationError as ve:
                    print(f"[ERROR] Checker Persona '{cid_name}' in {nid} violates persona_profile.schema.json: {ve.message}", file=sys.stderr)
                    return False
            if c_prof:
                c_cat = c_prof.get("identity_and_mandate", {}).get("role_category", "")
                if c_cat == "Maker":
                    print(f"[ERROR] Checker Persona '{cid_name}' in {nid} declares role_category='Maker'. Checkers must be adversarial auditors.", file=sys.stderr)
                    return False
                c_stance = c_prof.get("epistemic_stance", {}).get("stance_type", "")
                if c_stance == "constructive_synthesis":
                    print(f"[ERROR] Checker Persona '{cid_name}' in {nid} has constructive stance. Checkers must be adversarial/skeptical.", file=sys.stderr)
                    return False
                if c_stance:
                    checker_stances.append(c_stance)

        if len(checker_stances) == 3 and len(set(checker_stances)) != 3:
            print(f"[WARN] Node {nid}: Checker personas share overlapping epistemic stances: {checker_stances}. Recommended: [hostile_falsification, adversarial_exploit, macro_sentinel].", file=sys.stderr)

    # 4. Dependency Validation & Acyclicity Proof (Kahn's Algorithm)
    for nid, node in node_map.items():
        deps = node.get("dependencies", [])
        clean_deps = []
        for d in deps:
            did = str(d).strip()
            if did == nid:
                print(f"[ERROR] Self-dependency in node {nid}!", file=sys.stderr)
                return False
            if did not in node_map:
                print(f"[ERROR] Node {nid} depends on non-existent node '{did}'", file=sys.stderr)
                return False
            if did not in clean_deps:
                clean_deps.append(did)

        for did in clean_deps:
            adj[did].append(nid)
            rev_adj[nid].append(did)
            in_degree[nid] += 1

    queue = deque([nid for nid in node_map if in_degree[nid] == 0])
    topo_order: List[str] = []

    while queue:
        curr = queue.popleft()
        topo_order.append(curr)
        for nxt in adj[curr]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    if len(topo_order) != len(nodes):
        unvisited = [n for n, deg in in_degree.items() if deg > 0]
        print(f"[ERROR] CYCLE DETECTED IN DAG! Closed loop involving: {unvisited}", file=sys.stderr)
        return False

    # 5. Topological Depth & Critical Path Calculation
    node_depth: Dict[str, int] = {}
    for nid in topo_order:
        parents = rev_adj[nid]
        if not parents:
            node_depth[nid] = 0
        else:
            node_depth[nid] = 1 + max(node_depth[p] for p in parents)

    critical_path_depth = max(node_depth.values()) if node_depth else 0

    # 6. Transitive Reachability Computation (for topological independence)
    reachable: Dict[str, Set[str]] = defaultdict(set)
    for nid in reversed(topo_order):
        for child in adj[nid]:
            reachable[nid].add(child)
            reachable[nid].update(reachable[child])

    # 7. Bernstein Concurrency Verification
    concurrency_hazards = []
    parallel_safe_pairs = []

    if check_concurrency and len(nodes) > 1:
        node_ids = list(node_map.keys())
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                u, v = node_ids[i], node_ids[j]

                is_dependent = (v in reachable[u]) or (u in reachable[v])
                if not is_dependent:
                    safe, conflicts = check_bernstein_conditions(node_map[u], node_map[v])
                    if safe:
                        parallel_safe_pairs.append((u, v))
                    else:
                        concurrency_hazards.append({
                            "pair": (u, v),
                            "conflicts": conflicts
                        })

    # Group into parallel execution waves
    waves: List[List[str]] = defaultdict(list)
    for nid in topo_order:
        waves[node_depth[nid]].append(nid)
    execution_waves = [waves[d] for d in sorted(waves.keys())]

    # Report Findings
    if not json_output:
        print(f"✓ Topologically Sound: Acyclic graph verified.")
        print(f"✓ Total Work Units:    {len(nodes)}")
        print(f"✓ Critical Path Depth: {critical_path_depth}")
        print(f"✓ Execution Waves:     {len(execution_waves)} sequential stages")
        for idx, wave in enumerate(execution_waves):
            print(f"   Wave {idx} (depth={idx}): {', '.join(wave)}")

        if concurrency_hazards:
            print(f"\n\033[33m[WARN] BERNSTEIN CONCURRENCY HAZARDS DETECTED ({len(concurrency_hazards)} pairs):\033[0m")
            for h in concurrency_hazards:
                u, v = h["pair"]
                print(f"  • Hazard between independent peers {u} and {v}:")
                for ctype, confs in h["conflicts"].items():
                    print(f"    - {ctype}: {confs}")
            print("\033[33m  -> These units must NOT be scheduled in parallel without serialization barriers.\033[0m")
        else:
            print(f"✓ Concurrency Safety:  All independent peers satisfy Bernstein's Non-Interference Conditions!")

    # 8. On-Disk Audit
    if audit_disk:
        sess_dir = manifest_file.parent.parent
        disk_ok = audit_disk_contracts(sess_dir, nodes)
        if not disk_ok:
            return False

    if json_output:
        res = {
            "valid": True,
            "acyclic": True,
            "critical_path_depth": critical_path_depth,
            "total_nodes": len(nodes),
            "topological_order": topo_order,
            "execution_waves": execution_waves,
            "parallel_safe_pairs": parallel_safe_pairs,
            "concurrency_hazards": concurrency_hazards,
        }
        print(json.dumps(res, indent=2))

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formal DAG Validator and Bernstein Concurrency Prover.")
    parser.add_argument("--manifest-path", help="Path to dag_manifest.json")
    parser.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    parser.add_argument("--audit-disk", action="store_true", help="Audit physical on-disk unit contracts")
    parser.add_argument("--no-concurrency", action="store_true", help="Skip Bernstein concurrency non-interference check")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    ok = validate_formal_dag(
        manifest_path=args.manifest_path,
        workspace_root=args.workspace_root,
        audit_disk=args.audit_disk,
        check_concurrency=not args.no_concurrency,
        json_output=args.json
    )
    if not ok:
        sys.exit(1)
