#!/usr/bin/env python3
"""
socratic_dialogue.py - Formal Engine for Layered Input Clarification & Execution-Phase Assumption Invalidation.

Enforces:
1. Phase 1.5 Layered Socratic Input Clarification Gate (invoked strictly post-Cartography and pre-DAG).
2. Execution-Phase Dynamic Discovery Assumption Invalidation Human Gate (blocks AWU execution/adjudication until human resolution).
3. Strictly ONE question per dialogue turn.
4. Exhaustive evaluation of all options (pros, cons, trade-off analysis).
5. Best option presented FIRST and marked '(Recommended)'.
6. Plain human language with inline demystification of every technical term in parentheses or commas.
7. Machine-readable validation against socratic_dialogue.schema.json and on-disk auditability.
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    from dag_utils import find_latest_session, find_resource_file
    from input_gap_auditor import audit_specification_text, audit_session_cartography
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    from dag_utils import find_latest_session, find_resource_file
    from input_gap_auditor import audit_specification_text, audit_session_cartography


# Known technical terms requiring inline demystification (in parentheses or commas)
TECHNICAL_JARGON_TERMS = [
    "idempotency",
    "idempotent",
    "concurrency",
    "mutex",
    "pessimistic lock",
    "isolation level",
    "serializable",
    "dag",
    "directed acyclic graph",
    "ast",
    "pbt",
    "property-based testing",
    "smt",
    "symbolic execution",
    "backpressure",
    "circuit breaker",
    "fencing token",
    "outbox pattern",
    "time-to-live",
    "ttl",
    "rate limiting",
    "read-after-write",
    "write-after-write",
    "write-after-read",
]


def check_plain_language_demystification(text: str) -> Tuple[bool, List[str]]:
    """
    Verifies that technical terms are accompanied by immediate inline explanations
    in parentheses (e.g. 'idempotency (meaning ...)') or comma-separated appositives.
    """
    lower = text.lower()
    missing_explanations = []

    for term in TECHNICAL_JARGON_TERMS:
        # Check if term appears as a standalone word
        pattern = r"\b" + re.escape(term) + r"\b"
        match = re.search(pattern, lower)
        if match:
            start_pos = match.end()
            # Look at the succeeding 100 characters for an opening parenthesis or comma explanation
            succeeding_window = lower[start_pos:start_pos + 120]
            # Heuristic: must have parenthesis right after or comma explanation
            has_parenthetical = bool(re.search(r"^\s*[\(\,\—\-]", succeeding_window))
            if not has_parenthetical:
                missing_explanations.append(term)

    is_compliant = (len(missing_explanations) == 0)
    return is_compliant, missing_explanations


def validate_socratic_dialogue_item(item: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Formally validates an individual Socratic dialogue item against the mandatory constraints:
    1. Single question rule.
    2. Options count >= 2.
    3. First option is recommended.
    4. Non-empty pros, cons, and trade-off analysis for every option.
    5. Plain language demystification.
    """
    errors: List[str] = []

    q = item.get("question", "").strip()
    if not q:
        errors.append("Question is empty.")
    elif not q.endswith("?"):
        errors.append(f"Question must end with a question mark: '{q}'")

    # Single-question discipline: forbid prompt-stuffing multiple questions
    q_marks = q.count("?")
    if q_marks > 1:
        errors.append(f"SINGLE QUESTION RULE VIOLATION: Dialogue contains {q_marks} question marks. Strictly ONE question per dialogue turn is permitted.")

    options = item.get("options", [])
    if len(options) < 2:
        errors.append(f"OPTIONS COUNT VIOLATION: Dialogue must present at least 2 evaluated options. Found: {len(options)}")
    else:
        # First option must be recommended
        first_opt = options[0]
        if not first_opt.get("is_recommended", False):
            errors.append("RECOMMENDATION HIERARCHY VIOLATION: The first option (Index 0) MUST have is_recommended=True.")
        if not first_opt.get("label", "").startswith("(Recommended)"):
            first_opt["label"] = f"(Recommended) {first_opt.get('label', '')}".strip()

        # Subsequent options must NOT be recommended
        for idx, opt in enumerate(options[1:], start=1):
            if opt.get("is_recommended", False):
                errors.append(f"RECOMMENDATION HIERARCHY VIOLATION: Option {idx} cannot be marked recommended. Only Option 0 can be recommended.")

        # Each option must have pros, cons, trade_off_analysis
        for idx, opt in enumerate(options):
            oid = opt.get("id", f"OPTION-{idx+1}")
            if not opt.get("pros"):
                errors.append(f"Option {oid} must include at least one positive benefit ('pros').")
            if not opt.get("cons"):
                errors.append(f"Option {oid} must include at least one trade-off or downside ('cons').")
            if not opt.get("trade_off_analysis", "").strip():
                errors.append(f"Option {oid} must include a thorough 'trade_off_analysis'.")

    # Plain language check
    full_text = q + " " + item.get("context_and_reality", "") + " " + " ".join([o.get("plain_language_explanation", "") for o in options])
    pl_ok, terms = check_plain_language_demystification(full_text)
    if not pl_ok:
        # Warning/Flag: recorded in dialogue but doesn't hard-crash if minor
        item["plain_language_warnings"] = [f"Technical term '{t}' should have immediate inline explanation in parentheses" for t in terms]

    item["plain_language_verified"] = pl_ok
    is_valid = (len(errors) == 0)
    return is_valid, errors
def validate_socratic_manifest(manifest_data: Dict[str, Any], session_dir: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """Validates the full socratic dialogues ledger against socratic_dialogue.schema.json."""
    if not HAS_JSONSCHEMA:
        return True, []
    schema_file = find_resource_file("socratic_dialogue.schema.json", session_dir)
    if not schema_file or not schema_file.exists():
        return True, []
    try:
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        validator = jsonschema.Draft7Validator(schema)
        errors = [f"{e.message} at path: {list(e.path)}" for e in validator.iter_errors(manifest_data)]
        return len(errors) == 0, errors
    except Exception as ex:
        return False, [str(ex)]



def formulate_dialogues_from_gaps(detected_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms detected input gaps into a series of strictly structured Socratic dialogues.
    Each gap produces a single-question dialogue with evaluated options and (Recommended) first.
    """
    dialogues: List[Dict[str, Any]] = []

    for idx, gap in enumerate(detected_gaps, start=1):
        gid = gap.get("gap_id", f"GAP-{idx:03d}")
        gname = gap.get("name", "Specification Ambiguity")
        category = gap.get("category", "General")
        desc = gap.get("description", "")

        # Layer determination
        if "Class 1" in category:
            layer = "Layer 1: Structural & Boundary Audit"
            question = f"How should we formally establish the boundary rules and constraints for {gname.lower()} to prevent system failures?"
            options = [
                {
                    "id": "OPT-1",
                    "label": f"(Recommended) Enforce strict verification rules and positive constraints for {gname}",
                    "is_recommended": True,
                    "plain_language_explanation": f"We apply strict boundary checks (rules that prevent invalid numbers, empty inputs, or missing data from entering the system) directly at the entrance of each function.",
                    "pros": [
                        "Completely eliminates invalid input hazards before processing begins",
                        "Aligns with verified system invariants mapped during initial cartography",
                        "Guarantees that subagents will not synthesize hallucinated or permissive fallbacks"
                    ],
                    "cons": [
                        "Rejects malformed input early, requiring callers to send well-formed parameters"
                    ],
                    "trade_off_analysis": "Strict boundary enforcement prevents silent data corruption and unexpected crashes downstream. It provides the highest long-term maintainability."
                },
                {
                    "id": "OPT-2",
                    "label": f"Apply safe, documented non-blocking fallback defaults for {gname}",
                    "is_recommended": False,
                    "plain_language_explanation": f"We define conservative standard values (safe default settings) whenever parameters are omitted, logging a clear warning message.",
                    "pros": [
                        "Provides higher tolerance for lenient external callers",
                        "Reduces setup friction for simple test scenarios"
                    ],
                    "cons": [
                        "May mask client-side bugs where callers forgot to pass important parameters",
                        "Introduces implicit assumptions that might surprise future developers"
                    ],
                    "trade_off_analysis": "While convenient for prototypes, implicit defaults risk masking upstream defects. Recommended only if caller interfaces cannot be updated."
                }
            ]
        elif "Class 2" in category:
            layer = "Layer 2: Invariant & Failure-Semantics Audit"
            question = f"Which standardized data format and error handling structure should we declare for {gname.lower()}?"
            options = [
                {
                    "id": "OPT-1",
                    "label": f"(Recommended) Standardize on typed UTF-8 JSON schemas with explicit error codes",
                    "is_recommended": True,
                    "plain_language_explanation": "We use UTF-8 text encoding (the universal standard for readable characters) and structured JSON error responses (a clean format describing exactly why an action failed).",
                    "pros": [
                        "Predictable machine-readable contracts across all components",
                        "Precise error attribution for debugging and automated retries",
                        "Strict alignment with industry standards (such as RFC 7807 problem details)"
                    ],
                    "cons": [
                        "Requires defining typed error structures up front"
                    ],
                    "trade_off_analysis": "Standardized schema definitions eliminate guesswork between makers and checkers, ensuring reliable cross-component interaction."
                },
                {
                    "id": "OPT-2",
                    "label": "Use simple plain-text error messages and lenient serialization",
                    "is_recommended": False,
                    "plain_language_explanation": "We return plain readable error sentences without a formal machine-readable schema structure.",
                    "pros": [
                        "Minimal upfront schema modeling"
                    ],
                    "cons": [
                        "Callers cannot programmatically differentiate between error types",
                        "Violates typed contract verification in automated checker panels"
                    ],
                    "trade_off_analysis": "Plain text is easy for humans to read informally, but breaks automated verification panels and machine clients."
                }
            ]
        else:
            # Class 3 or other
            layer = "Layer 2: Invariant & Failure-Semantics Audit"
            question = f"What exact safety mechanisms and timeout boundaries should protect {gname.lower()} during network or system disruptions?"
            options = [
                {
                    "id": "OPT-1",
                    "label": f"(Recommended) Implement bounded timeouts with unique tracking tokens for safe retries",
                    "is_recommended": True,
                    "plain_language_explanation": "We set a hard deadline on external calls (timeouts) and attach an idempotency token (a unique tracking tag ensuring an action is never executed twice by mistake).",
                    "pros": [
                        "Prevents duplicate payments or state mutations during network retries",
                        "Prevents runaway delays and system lockups when remote services slow down",
                        "Mathematically guarantees safe re-execution after dropouts"
                    ],
                    "cons": [
                        "Requires maintaining a temporary ledger of processed tracking tokens"
                    ],
                    "trade_off_analysis": "Idempotency tokens and strict timeouts are essential in distributed systems to prevent double-charging or cascading service outages."
                },
                {
                    "id": "OPT-2",
                    "label": "Rely on basic synchronous network calls with unlimited wait times",
                    "is_recommended": False,
                    "plain_language_explanation": "We make standard direct calls without timeout caps or deduplication keys.",
                    "pros": [
                        "Simpler initial implementation without token storage"
                    ],
                    "cons": [
                        "High risk of double execution if network requests drop and are retried",
                        "Can cause system deadlocks (where processes freeze waiting forever for an answer)"
                    ],
                    "trade_off_analysis": "Exposes the system to catastrophic stalls and duplicate state mutations under real-world network turbulence."
                }
            ]

        dialogue_item = {
            "dialogue_id": f"SOCRATIC-{idx:03d}",
            "unit_id": "GLOBAL_INPUT",
            "layer": layer,
            "question_index": idx,
            "total_in_series": len(detected_gaps),
            "question": question,
            "context_and_reality": f"During initial codebase mapping (Cartography), we audited the project inputs against authoritative engineering standards. We identified an unstated specification gap regarding {gname.lower()} ({desc}). To prevent guesswork and hallucinations, this decision must be settled before task planning begins.",
            "options": options,
            "status": "PENDING",
            "human_response": None
        }
        validate_socratic_dialogue_item(dialogue_item)
        dialogues.append(dialogue_item)

    return dialogues


def audit_layered_input_clarification(
    session_dir: Optional[Path] = None,
    workspace_root: Optional[str] = None,
    spec_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes Phase 1.5 Layered Socratic Input Clarification Gate.
    Must be invoked strictly AFTER Cartography (Phase 1) and BEFORE DAG Decomposition (Phase 2).
    """
    sess = session_dir or find_latest_session(workspace_root)
    if not sess or not sess.exists():
        return {
            "status": "ERROR",
            "is_blocking": True,
            "explanation": "No active .omp_wip session directory found."
        }

    cart_dir = sess / "00_cartography"
    cart_dir.mkdir(parents=True, exist_ok=True)
    dialogues_json = cart_dir / "socratic_dialogues.json"
    dialogues_md = cart_dir / "socratic_dialogues.md"

    # If dialogues already exist on disk and have been formulated or resolved, load them
    if dialogues_json.exists() and not spec_text:
        try:
            stored_manifest = json.loads(dialogues_json.read_text(encoding="utf-8"))
            dialogues = stored_manifest.get("dialogues", [])
            stored_status = stored_manifest.get("status")
            if stored_status in ["RESOLVED", "CLEAN_PASS"] or len(dialogues) > 0:
                pending_count = sum(1 for d in dialogues if d.get("status") != "RESOLVED")
                is_resolved = (pending_count == 0) and (stored_status != "PENDING" or len(dialogues) > 0)
                status = stored_status if stored_status in ["RESOLVED", "CLEAN_PASS"] else ("RESOLVED" if is_resolved else "IN_PROGRESS")
                _sync_manifest_input_clarification(sess, status=status, total=len(dialogues), resolved=len(dialogues) - pending_count)
                return {
                    "status": status,
                    "is_blocking": not (status in ["RESOLVED", "CLEAN_PASS"]),
                    "session_path": str(sess),
                    "total_questions": len(dialogues),
                    "resolved_questions": len(dialogues) - pending_count,
                    "pending_questions": pending_count,
                    "dialogues": dialogues,
                    "explanation": "All input clarification questions resolved." if (status in ["RESOLVED", "CLEAN_PASS"]) else f"{pending_count} Socratic dialogue question(s) pending human resolution."
                }
        except Exception:
            pass
    # Perform Layer 1 & 2 audit on cartography / spec
    if spec_text:
        iga_res = audit_specification_text(spec_text)
    else:
        iga_res = audit_session_cartography(sess, workspace_root)

    gaps = iga_res.get("detected_gaps", [])

    if not gaps:
        # Zero gaps detected: Clean Pass
        manifest_data = {
            "session_id": sess.name,
            "dialogue_phase": "phase_1_5_input_clarification",
            "total_questions": 0,
            "resolved_questions": 0,
            "status": "CLEAN_PASS",
            "dialogues": []
        }
        valid, schema_errs = validate_socratic_manifest(manifest_data, sess)
        if not valid:
            print(f"[WARN] Socratic manifest schema warnings: {schema_errs}", file=sys.stderr)
        dialogues_json.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        _render_dialogues_markdown(dialogues_md, manifest_data)
        _sync_manifest_input_clarification(sess, status="CLEAN_PASS", total=0, resolved=0)
        return {
            "status": "CLEAN_PASS",
            "is_blocking": False,
            "session_path": str(sess),
            "total_questions": 0,
            "resolved_questions": 0,
            "pending_questions": 0,
            "dialogues": [],
            "explanation": "PASSED: Zero unverified assumptions or input gaps detected. Specification is contractually sound for DAG decomposition."
        }

    # Formulate Layer 3 Socratic Dialogues
    dialogues = formulate_dialogues_from_gaps(gaps)
    # Mark first dialogue ACTIVE
    if dialogues:
        dialogues[0]["status"] = "ACTIVE"

    manifest_data = {
        "session_id": sess.name,
        "dialogue_phase": "phase_1_5_input_clarification",
        "total_questions": len(dialogues),
        "resolved_questions": 0,
        "status": "PENDING",
        "dialogues": dialogues
    }

    valid, schema_errs = validate_socratic_manifest(manifest_data, sess)
    if not valid:
        print(f"[WARN] Socratic manifest schema warnings: {schema_errs}", file=sys.stderr)
    dialogues_json.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    _render_dialogues_markdown(dialogues_md, manifest_data)
    _sync_manifest_input_clarification(sess, status="PENDING", total=len(dialogues), resolved=0)

    return {
        "status": "PENDING",
        "is_blocking": True,
        "session_path": str(sess),
        "total_questions": len(dialogues),
        "resolved_questions": 0,
        "pending_questions": len(dialogues),
        "dialogues": dialogues,
        "explanation": f"LAYERED INPUT CLARIFICATION REQUIRED: {len(dialogues)} critical question(s) must be resolved via Socratic dialogue before DAG decomposition can proceed."
    }


def step_socratic_dialogue(
    session_dir: Optional[Path] = None,
    workspace_root: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Returns the single next pending Socratic dialogue question to present to the user.
    Enforces strictly ONE question per turn.
    """
    sess = session_dir or find_latest_session(workspace_root)
    if not sess:
        return None

    dialogues_json = sess / "00_cartography" / "socratic_dialogues.json"
    if not dialogues_json.exists():
        return None

    try:
        data = json.loads(dialogues_json.read_text(encoding="utf-8"))
        for d in data.get("dialogues", []):
            if d.get("status") in ["ACTIVE", "PENDING"]:
                return d
    except Exception:
        return None
    return None

def format_socratic_for_ask(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats an individual Socratic dialogue item into OMP ask tool parameters.
    Guarantees clean non-duplicated labels, rich trade-off descriptions, and recommended index 0.
    """
    ask_options = []
    for opt in item.get("options", []):
        clean_lbl = re.sub(r"^\(Recommended\)\s*", "", opt.get("label", ""))
        desc_parts = []
        if opt.get("plain_language_explanation"):
            desc_parts.append(opt.get("plain_language_explanation"))
        if opt.get("trade_off_analysis"):
            desc_parts.append(f"Trade-off: {opt.get('trade_off_analysis')}")
        ask_options.append({
            "label": clean_lbl,
            "description": " ".join(desc_parts) if desc_parts else None
        })
    return {
        "id": item.get("dialogue_id", "SOCRATIC-001"),
        "question": item.get("question", ""),
        "header": item.get("layer", "Input Clarification"),
        "recommended": 0,
        "options": ask_options
    }



def resolve_socratic_dialogue(
    dialogue_id: str,
    selected_option_id: str,
    custom_input: Optional[str] = None,
    decision_rationale: Optional[str] = None,
    session_dir: Optional[Path] = None,
    workspace_root: Optional[str] = None
) -> Dict[str, Any]:
    """
    Records human decision for a specific Socratic dialogue, marking it RESOLVED.
    Advances the pointer to activate the next dialogue in the series.
    """
    sess = session_dir or find_latest_session(workspace_root)
    if not sess:
        return {"success": False, "error": "Session not found"}

    dialogues_json = sess / "00_cartography" / "socratic_dialogues.json"
    dialogues_md = sess / "00_cartography" / "socratic_dialogues.md"
    if not dialogues_json.exists():
        return {"success": False, "error": "No dialogues manifest found"}

    data = json.loads(dialogues_json.read_text(encoding="utf-8"))
    dialogues = data.get("dialogues", [])

    target = None
    next_item = None
    for idx, d in enumerate(dialogues):
        if d.get("dialogue_id") == dialogue_id:
            target = d
            # Find next pending
            for nxt in dialogues[idx + 1:]:
                if nxt.get("status") == "PENDING":
                    next_item = nxt
                    break
            break

    if not target:
        return {"success": False, "error": f"Dialogue {dialogue_id} not found"}

    # Find matching option
    sel_opt = next((o for o in target.get("options", []) if o.get("id") == selected_option_id), None)
    opt_label = sel_opt.get("label", selected_option_id) if sel_opt else selected_option_id

    target["status"] = "RESOLVED"
    target["human_response"] = {
        "selected_option_id": selected_option_id,
        "selected_option_label": opt_label,
        "custom_input": custom_input,
        "decision_rationale": decision_rationale or "Confirmed via formal Socratic dialogue.",
        "answered_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if next_item:
        next_item["status"] = "ACTIVE"

    resolved_count = sum(1 for d in dialogues if d.get("status") == "RESOLVED")
    all_done = (resolved_count == len(dialogues))
    data["resolved_questions"] = resolved_count
    data["status"] = "RESOLVED" if all_done else "IN_PROGRESS"

    dialogues_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _render_dialogues_markdown(dialogues_md, data)
    _sync_manifest_input_clarification(sess, status=data["status"], total=len(dialogues), resolved=resolved_count)

    return {
        "success": True,
        "resolved_dialogue_id": dialogue_id,
        "is_all_resolved": all_done,
        "next_dialogue_id": next_item.get("dialogue_id") if next_item else None,
        "total_questions": len(dialogues),
        "resolved_questions": resolved_count
    }


def register_assumption_invalidation(
    unit_id: str,
    assumption_summary: str,
    discovery_evidence: str,
    proposed_options: Optional[List[Dict[str, Any]]] = None,
    session_dir: Optional[Path] = None,
    workspace_root: Optional[str] = None
) -> Dict[str, Any]:
    """
    Registers an Execution-Phase Assumption Invalidation with a MANDATORY HUMAN GATE.
    1. Blocks the AWU in dag_manifest.json (status='BLOCKED').
    2. Registers the invalidation record.
    3. Formulates a dedicated Socratic Dialogue in plain human language with evaluated options and (Recommended) first.
    4. Halts all automated progress until human sign-off.
    """
    sess = session_dir or find_latest_session(workspace_root)
    if not sess:
        return {"success": False, "error": "Session not found"}

    manifest_file = sess / "01_dag" / "dag_manifest.json"
    if not manifest_file.exists():
        return {"success": False, "error": "dag_manifest.json not found"}

    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    nodes = manifest_data.get("nodes", [])

    target_node = next((n for n in nodes if n.get("id") == unit_id), None)
    if not target_node:
        return {"success": False, "error": f"Unit {unit_id} not found in manifest"}

    # Block unit immediately
    target_node["status"] = "BLOCKED"

    invalidation_list = manifest_data.setdefault("invalidated_assumptions", [])
    inval_id = f"INVAL-{len(invalidation_list) + 1:03d}"
    dialogue_id = f"SOCRATIC-INVAL-{inval_id}"

    # Build options if not provided
    if not proposed_options:
        proposed_options = [
            {
                "id": "OPT-1",
                "label": "(Recommended) Re-align task contracts and update implementation to reflect discovered reality",
                "is_recommended": True,
                "plain_language_explanation": "We update the work unit contract (the formal list of guarantees and constraints) to accommodate the new empirical discovery, without breaking external callers.",
                "pros": [
                    "Directly resolves the contradiction using verified on-disk facts",
                    "Preserves systemic integrity without inventing imaginary behaviors",
                    "Allows execution to safely resume once contracts are updated"
                ],
                "cons": [
                    "Requires minor adjustments to unit test assertions"
                ],
                "trade_off_analysis": "Re-aligning the contract grounded in real findings eliminates the risk of synthesizing hallucinated workarounds."
            },
            {
                "id": "OPT-2",
                "label": "Trigger a Bounded Graph Addition (BGA) to insert an upstream adapter or migration task",
                "is_recommended": False,
                "plain_language_explanation": "We add an extra task into our workflow roadmap (a Bounded Graph Addition) specifically to bridge the gap between the old expectation and the new finding.",
                "pros": [
                    "Leaves the current unit's scope strictly untouched",
                    "Isolates the compatibility layer in a dedicated atomic work unit"
                ],
                "cons": [
                    "Increases graph depth by 1 and adds a new work unit to complete"
                ],
                "trade_off_analysis": "Appropriate only if the discovered change has wide blast radius affecting multiple independent modules."
            }
        ]

    # Validate first option recommended
    if not proposed_options[0].get("is_recommended", False):
        proposed_options[0]["is_recommended"] = True
    if not proposed_options[0].get("label", "").startswith("(Recommended)"):
        proposed_options[0]["label"] = f"(Recommended) {proposed_options[0].get('label', '')}".strip()

    dialogue_item = {
        "dialogue_id": dialogue_id,
        "unit_id": unit_id,
        "layer": "Execution Discovery: Assumption Invalidation",
        "question_index": 1,
        "total_in_series": 1,
        "question": f"How should we update the implementation and contracts for unit {unit_id} to resolve the newly discovered reality?",
        "context_and_reality": f"During active execution of work unit {unit_id}, new empirical evidence was uncovered that directly invalidates a prior assumption: '{assumption_summary}'. Evidence observed: {discovery_evidence}. Under the Non-Negotiable Human Gate rule, autonomous execution is halted until this decision is formally resolved.",
        "invalidated_prior_assumption": assumption_summary,
        "discovery_evidence": discovery_evidence,
        "options": proposed_options,
        "status": "ACTIVE",
        "human_response": None
    }
    validate_socratic_dialogue_item(dialogue_item)

    inval_record = {
        "invalidation_id": inval_id,
        "unit_id": unit_id,
        "assumption_summary": assumption_summary,
        "discovery_evidence": discovery_evidence,
        "status": "ACTIVE_BLOCKER",
        "human_gate_status": "PENDING_HUMAN_DIALOGUE",
        "dialogue_id": dialogue_id,
        "resolution_summary": None,
        "resolved_at": None
    }
    invalidation_list.append(inval_record)

    # Save manifest
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    # Save dialogue file in unit directory and cartography ledger
    units_dir = sess / "units"
    unit_dir = units_dir / f"{unit_id}_{target_node.get('slug', '')}"
    if not unit_dir.exists() and units_dir.exists():
        for d in units_dir.iterdir():
            if d.is_dir() and (d.name == unit_id or d.name.startswith(f"{unit_id}_")):
                unit_dir = d
                break

    if unit_dir and unit_dir.exists():
        (unit_dir / "invalidation_dialogue.json").write_text(json.dumps(dialogue_item, indent=2), encoding="utf-8")

    # Update session ledger
    inval_ledger = sess / "01_dag" / "assumption_invalidations.json"
    inval_ledger.write_text(json.dumps(invalidation_list, indent=2), encoding="utf-8")

    return {
        "success": True,
        "invalidation_id": inval_id,
        "unit_id": unit_id,
        "status": "BLOCKED_MANDATORY_HUMAN_GATE",
        "dialogue": dialogue_item,
        "explanation": f"MANDATORY HUMAN GATE TRIGGERED: Unit {unit_id} halted. Prior assumption '{assumption_summary}' invalidated. Socratic inquiry waiting for human decision."
    }


def resolve_assumption_invalidation(
    invalidation_id: str,
    selected_option_id: str,
    resolution_summary: str,
    session_dir: Optional[Path] = None,
    workspace_root: Optional[str] = None
) -> Dict[str, Any]:
    """
    Formally records the human resolution of an assumption invalidation gate.
    Unblocks the AWU and updates learnings and briefings.
    """
    sess = session_dir or find_latest_session(workspace_root)
    if not sess:
        return {"success": False, "error": "Session not found"}

    manifest_file = sess / "01_dag" / "dag_manifest.json"
    if not manifest_file.exists():
        return {"success": False, "error": "dag_manifest.json not found"}

    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    invalidation_list = manifest_data.get("invalidated_assumptions", [])

    inval = next((i for i in invalidation_list if i.get("invalidation_id") == invalidation_id), None)
    if not inval:
        return {"success": False, "error": f"Invalidation record {invalidation_id} not found"}

    unit_id = inval.get("unit_id")
    inval["status"] = "RESOLVED"
    inval["human_gate_status"] = "RESOLVED_BY_HUMAN"
    inval["resolution_summary"] = resolution_summary
    inval["resolved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Unblock target unit
    for n in manifest_data.get("nodes", []):
        if n.get("id") == unit_id:
            n["status"] = "IN_PROGRESS"

    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    # Update unit learnings.jsonl and briefing.md
    units_dir = sess / "units"
    if units_dir.exists():
        for udir in units_dir.iterdir():
            if udir.is_dir() and (udir.name == unit_id or udir.name.startswith(f"{unit_id}_")):
                learnings_file = udir / "learnings.jsonl"
                learning_entry = {
                    "epoch": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "type": "ASSUMPTION_INVALIDATION_RESOLUTION",
                    "invalidation_id": invalidation_id,
                    "invalidated_assumption": inval.get("assumption_summary"),
                    "human_resolution": resolution_summary,
                    "selected_option": selected_option_id
                }
                with open(learnings_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(learning_entry) + "\n")

                briefing_md = udir / "briefing.md"
                if briefing_md.exists():
                    note = f"\n\n### [HUMAN GATE RESOLUTION: {invalidation_id}]\n- **Invalidated Assumption**: {inval.get('assumption_summary')}\n- **Resolution**: {resolution_summary}\n"
                    with open(briefing_md, "a", encoding="utf-8") as f:
                        f.write(note)
                break

    return {
        "success": True,
        "invalidation_id": invalidation_id,
        "unit_id": unit_id,
        "status": "RESOLVED",
        "explanation": f"HUMAN GATE RESOLVED: Unit {unit_id} unblocked. Assumption updated to '{resolution_summary}'."
    }


def _sync_manifest_input_clarification(session_dir: Path, status: str, total: int, resolved: int):
    manifest_file = session_dir / "01_dag" / "dag_manifest.json"
    if manifest_file.exists():
        try:
            m = json.loads(manifest_file.read_text(encoding="utf-8"))
            m["input_clarification"] = {
                "status": status,
                "total_questions": total,
                "resolved_questions": resolved,
                "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat() if status in ["RESOLVED", "CLEAN_PASS"] else None,
                "dialogues_file": "00_cartography/socratic_dialogues.json"
            }
            manifest_file.write_text(json.dumps(m, indent=2), encoding="utf-8")
        except Exception:
            pass


def _render_dialogues_markdown(md_path: Path, manifest: Dict[str, Any]):
    lines = [
        "# Formal Socratic Input Clarification Ledger",
        "",
        f"- **Session ID**: `{manifest.get('session_id')}`",
        f"- **Dialogue Phase**: `{manifest.get('dialogue_phase')}`",
        f"- **Status**: `{manifest.get('status')}`",
        f"- **Total Inquiries**: {manifest.get('total_questions', 0)}",
        f"- **Resolved**: {manifest.get('resolved_questions', 0)}",
        "",
        "---",
        ""
    ]

    dialogues = manifest.get("dialogues", [])
    if not dialogues:
        lines.append("*Zero unverified assumptions or input gaps detected. Cartography is contractually sound.*")
    else:
        for d in dialogues:
            lines.append(f"## {d.get('dialogue_id')}: {d.get('layer')} (Question {d.get('question_index')} of {d.get('total_in_series')})")
            lines.append(f"- **Status**: `{d.get('status')}`")
            lines.append(f"- **Context & Observable Reality**: {d.get('context_and_reality')}")
            lines.append(f"- **Target Question**: **{d.get('question')}**")
            lines.append("")
            lines.append("### Evaluated Options:")
            for o in d.get("options", []):
                rec_badge = " **(Recommended)**" if o.get("is_recommended") else ""
                lines.append(f"#### Option `{o.get('id')}`:{rec_badge} {o.get('label')}")
                lines.append(f"- **Explanation**: {o.get('plain_language_explanation')}")
                lines.append(f"- **Pros**:")
                for p in o.get("pros", []):
                    lines.append(f"  + {p}")
                lines.append(f"- **Cons**:")
                for c in o.get("cons", []):
                    lines.append(f"  - {c}")
                lines.append(f"- **Trade-off Analysis**: {o.get('trade_off_analysis')}")
                lines.append("")

            hr = d.get("human_response")
            if hr:
                lines.append("### Human Decision Record:")
                lines.append(f"- **Selected Option**: `{hr.get('selected_option_id')}` — {hr.get('selected_option_label')}")
                if hr.get("custom_input"):
                    lines.append(f"- **Custom User Input**: {hr.get('custom_input')}")
                lines.append(f"- **Rationale**: {hr.get('decision_rationale')}")
                lines.append(f"- **Answered At**: `{hr.get('answered_at')}`")
                lines.append("")
            lines.append("---")
            lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Formal Socratic Dialogue & Assumption Invalidation Engine.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit session cartography through Layered Input Clarification")
    p_audit.add_argument("--session-path", help="Path to .omp_wip session directory")
    p_audit.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    p_audit.add_argument("--spec-file", help="Path to raw spec file")
    p_audit.add_argument("--json", action="store_true", help="Emit JSON output")

    # step
    p_step = subparsers.add_parser("step", help="Get the next pending Socratic dialogue question (one-question discipline)")
    p_step.add_argument("--session-path", help="Session path")
    p_step.add_argument("--workspace-root", help="Workspace root")
    p_step.add_argument("--ask-format", action="store_true", help="Format output for direct OMP ask tool invocation")
    p_step.add_argument("--json", action="store_true", help="Emit JSON output")
    # resolve
    p_res = subparsers.add_parser("resolve", help="Record human answer for a Socratic dialogue question")
    p_res.add_argument("--dialogue-id", required=True, help="Dialogue ID (e.g. SOCRATIC-001)")
    p_res.add_argument("--option-id", required=True, help="Selected Option ID (e.g. OPT-1)")
    p_res.add_argument("--custom", help="Custom user clarification or rationale")
    p_res.add_argument("--session-path", help="Session path")
    p_res.add_argument("--workspace-root", help="Workspace root")
    p_res.add_argument("--json", action="store_true", help="Emit JSON output")

    # invalidate
    p_inval = subparsers.add_parser("invalidate", help="Register dynamic discovery assumption invalidation (Human Gate)")
    p_inval.add_argument("--unit-id", required=True, help="Unit ID (e.g. AWU-001)")
    p_inval.add_argument("--assumption", required=True, help="Summary of invalidated prior assumption")
    p_inval.add_argument("--evidence", required=True, help="Empirical discovery evidence or error trace")
    p_inval.add_argument("--session-path", help="Session path")
    p_inval.add_argument("--workspace-root", help="Workspace root")
    p_inval.add_argument("--json", action="store_true", help="Emit JSON output")

    # resolve-invalidation
    p_res_inval = subparsers.add_parser("resolve-invalidation", help="Resolve assumption invalidation Human Gate")
    p_res_inval.add_argument("--invalidation-id", required=True, help="Invalidation ID (e.g. INVAL-001)")
    p_res_inval.add_argument("--option-id", required=True, help="Selected Option ID (e.g. OPT-1)")
    p_res_inval.add_argument("--summary", required=True, help="Human resolution summary")
    p_res_inval.add_argument("--session-path", help="Session path")
    p_res_inval.add_argument("--workspace-root", help="Workspace root")
    p_res_inval.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args()

    if args.command == "audit":
        spec_text = None
        if args.spec_file:
            spec_text = Path(args.spec_file).read_text(encoding="utf-8")
        res = audit_layered_input_clarification(
            session_dir=Path(args.session_path).resolve() if args.session_path else None,
            workspace_root=args.workspace_root,
            spec_text=spec_text
        )
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
                # Auto-display active inquiry so user and agent immediately see the question
                next_q = step_socratic_dialogue(
                    session_dir=Path(args.session_path).resolve() if args.session_path else None,
                    workspace_root=args.workspace_root
                )
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
    elif args.command == "step":
        res = step_socratic_dialogue(
            session_dir=Path(args.session_path).resolve() if args.session_path else None,
            workspace_root=args.workspace_root
        )
        if not res:
            if args.json:
                print(json.dumps({"has_pending": False}))
            else:
                print("\033[32mZero pending Socratic dialogues. All input clarifications complete.\033[0m")
            sys.exit(0)

        if getattr(args, "ask_format", False):
            ask_payload = format_socratic_for_ask(res)
            print(json.dumps({"questions": [ask_payload]}, indent=2))
            sys.exit(0)
        elif args.json:
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
    elif args.command == "resolve":
        res = resolve_socratic_dialogue(
            dialogue_id=args.dialogue_id,
            selected_option_id=args.option_id,
            custom_input=args.custom,
            session_dir=Path(args.session_path).resolve() if args.session_path else None,
            workspace_root=args.workspace_root
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("success"):
                print(f"\033[32m✓ Socratic dialogue {args.dialogue_id} resolved with option {args.option_id}.\033[0m")
                if res.get("is_all_resolved"):
                    print("\033[32m✓ All input clarification questions resolved! Gate passed.\033[0m")
                else:
                    print(f"Next active question: {res.get('next_dialogue_id')}")
            else:
                print(f"\033[31m[ERROR] Failed to resolve dialogue: {res.get('error')}\033[0m", file=sys.stderr)
                sys.exit(1)

    elif args.command == "invalidate":
        res = register_assumption_invalidation(
            unit_id=args.unit_id,
            assumption_summary=args.assumption,
            discovery_evidence=args.evidence,
            session_dir=Path(args.session_path).resolve() if args.session_path else None,
            workspace_root=args.workspace_root
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("success"):
                print(f"\033[31m==> MANDATORY HUMAN GATE TRIGGERED: {res.get('invalidation_id')}\033[0m")
                print(f"Unit {args.unit_id} has been placed in BLOCKED status.")
                print(f"Invalidated Assumption: {args.assumption}")
                print(f"Evidence:               {args.evidence}")
                print(f"\033[33mSocratic dialogue queued. Human decision required before resuming execution.\033[0m")
            else:
                print(f"[ERROR] {res.get('error')}", file=sys.stderr)
                sys.exit(1)

    elif args.command == "resolve-invalidation":
        res = resolve_assumption_invalidation(
            invalidation_id=args.invalidation_id,
            selected_option_id=args.option_id,
            resolution_summary=args.summary,
            session_dir=Path(args.session_path).resolve() if args.session_path else None,
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


if __name__ == "__main__":
    main()
