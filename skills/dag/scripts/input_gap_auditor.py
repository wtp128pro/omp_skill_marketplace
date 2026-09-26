#!/usr/bin/env python3
"""
input_gap_auditor.py - Production Input Gap Analysis (IGA) & Plausibility Trap Auditor.

Mechanistic Grounding (Layer 5 of Operational Persona whitepaper):
Prevents the Plausibility Trap where unconstrained LLMs sample median completions from
cross-entropy pretraining to paper over missing specifications.

Audits input requirements and specifications against the Three Formal Input Gap Classes:
1. Class 1: Unstated Invariants & Boundary Preconditions (Sev-1 Blocking Veto)
   - Concurrency isolation, row-level locks, numeric bounds, nullability, zero-allocation constraints.
2. Class 2: Contractual & Semantic Ambiguities (Sev-2 Major Veto)
   - Serialization encodings, missing error schemas, unspecified return types, ambiguous ordering.
3. Class 3: Partial Failure Semantics & External System Timeouts (Sev-1 Blocking Veto)
   - Network timeout SLAs, unhandled dropouts, retry storms, un-fenced distributed locks, idempotency tokens.

Audit Output:
- Machine-verifiable JSON containing identified gaps, severities, and blocking status.
- Enforces the Sev-1 Blocking Veto Gate before Phase 2 AWU decomposition.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from dag_utils import find_latest_session
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.resolve()))
    try:
        from dag_utils import find_latest_session
    except ImportError:
        def find_latest_session(w: Optional[str] = None) -> Optional[Path]:
            return None


# Domain Heuristic Probe Signatures for Gap Detection
CLASS_1_PROBES = [
    {
        "id": "GAP-C1-01",
        "name": "Database Concurrency Isolation Level",
        "keywords": ["database", "postgres", "mysql", "sql", "transaction", "balance", "transfer", "deduct"],
        "required_invariants": ["isolation level", "serializable", "read committed", "select for update", "pessimistic lock", "atomic"],
        "severity": "Sev-1",
        "description": "Financial or transactional mutation specified without explicit database transaction isolation level or row-level locking (lost update hazard)."
    },
    {
        "id": "GAP-C1-02",
        "name": "Numeric & Domain Boundary Preconditions",
        "keywords": ["amount", "count", "index", "size", "offset", "limit", "rate", "cents"],
        "required_invariants": ["positive", "non-negative", "max", "min", "overflow", "> 0", "bound"],
        "severity": "Sev-1",
        "description": "Numeric parameters accepted without explicit lower/upper bounds, zero handling, or overflow protection."
    },
    {
        "id": "GAP-C1-03",
        "name": "Nullability & Empty Collection Invariants",
        "keywords": ["list", "array", "collection", "payload", "items", "tokens"],
        "required_invariants": ["empty", "null", "undefined", "zero items", "empty list", "non-empty"],
        "severity": "Sev-1",
        "description": "Collection or string input processed without declaring invariants for empty or missing values."
    }
]

CLASS_2_PROBES = [
    {
        "id": "GAP-C2-01",
        "name": "Strict Schema & Error Type Definitions",
        "keywords": ["api", "endpoint", "return", "status", "json", "response"],
        "required_invariants": ["error response", "error schema", "status code", "exception", "failure schema"],
        "severity": "Sev-2",
        "description": "Endpoint or public function specifies happy-path return without complete failure/error payload schemas."
    },
    {
        "id": "GAP-C2-02",
        "name": "Encoding & Serialization Standards",
        "keywords": ["payload", "file", "stream", "export", "token", "string"],
        "required_invariants": ["utf-8", "json", "binary", "base64", "mime", "encoding"],
        "severity": "Sev-2",
        "description": "Data exchange format lacks explicit character encoding, serialization framing, or mime-type specification."
    }
]

CLASS_3_PROBES = [
    {
        "id": "GAP-C3-01",
        "name": "Distributed Idempotency & Fencing Tokens",
        "keywords": ["settle", "payment", "charge", "transfer", "order", "webhook", "publish", "worker"],
        "required_invariants": ["idempotency", "idempotent", "fencing token", "deduplication", "unique constraint", "lock lease"],
        "severity": "Sev-1",
        "description": "State-mutating distributed request or payment processing lacks unique idempotency token and fencing guarantees (double-execution hazard)."
    },
    {
        "id": "GAP-C3-02",
        "name": "External Service Timeouts & Partial Failure Semantics",
        "keywords": ["http", "external", "client", "remote", "gateway", "service", "fetch", "post"],
        "required_invariants": ["timeout", "circuit breaker", "retry", "jitter", "sla", "fallback", "outbox", "asyncpg"],
        "severity": "Sev-1",
        "description": "Outbound synchronous network dependency declared without explicit timeout SLA, retry bounding, or decoupled outbox pattern."
    }
]


def audit_specification_text(spec_text: str) -> Dict[str, Any]:
    """
    Performs deterministic gap detection across text using domain-specific invariant checklists.
    """
    lower_text = spec_text.lower()
    detected_gaps: List[Dict[str, Any]] = []

    all_probes = [
        ("Class 1: Unstated Invariants & Boundary Preconditions", CLASS_1_PROBES),
        ("Class 2: Contractual & Semantic Ambiguities", CLASS_2_PROBES),
        ("Class 3: Partial Failure Semantics & External Timeouts", CLASS_3_PROBES)
    ]

    for category_name, probes in all_probes:
        for probe in probes:
            # Check if domain context is activated by keywords
            keyword_matches = [kw for kw in probe["keywords"] if re.search(r"\b" + re.escape(kw) + r"\b", lower_text)]
            if len(keyword_matches) >= 1:
                # Context is active; check if required invariants are declared
                invariant_matches = [inv for inv in probe["required_invariants"] if inv in lower_text]
                if not invariant_matches:
                    detected_gaps.append({
                        "gap_id": probe["id"],
                        "category": category_name,
                        "name": probe["name"],
                        "severity": probe["severity"],
                        "trigger_keywords": keyword_matches,
                        "missing_invariants": probe["required_invariants"],
                        "description": probe["description"],
                        "recommended_mitigation": f"Formally specify {probe['name']} before proceeding to implementation."
                    })

    # Evaluation against Grounding in Reputable Sources
    has_citations = any(kw in lower_text for kw in ["rfc", "ieee", "iso", "standard", "official docs", "documentation", "github.com", "spec"])

    sev1_count = sum(1 for g in detected_gaps if g["severity"] == "Sev-1")
    sev2_count = sum(1 for g in detected_gaps if g["severity"] == "Sev-2")

    is_blocking = (sev1_count > 0)
    verdict = "BLOCKING_VETO" if is_blocking else ("WARN_AMBIGUITY" if sev2_count > 0 else "CLEAN_PASS")

    return {
        "verdict": verdict,
        "is_blocking": is_blocking,
        "sev_1_count": sev1_count,
        "sev_2_count": sev2_count,
        "has_authoritative_citations": has_citations,
        "total_gaps_found": len(detected_gaps),
        "detected_gaps": detected_gaps,
        "explanation": (
            f"SEV-1 BLOCKING VETO: {sev1_count} critical input gap(s) detected. The Plausibility Trap dictates that code generation must be halted until invariants are declared."
            if is_blocking else
            f"PASSED WITH CAVEATS: {sev2_count} contractual ambiguities found. Non-blocking defaults may be applied with documentation."
            if sev2_count > 0 else
            "PASSED: Zero latent input gaps detected. Specification is contractually sound for AWU decomposition."
        )
    }


def audit_session_cartography(session_dir: Optional[Path] = None, workspace_root: Optional[str] = None) -> Dict[str, Any]:
    """Audits the active session's cartography files."""
    sess = session_dir or find_latest_session(workspace_root)
    if not sess or not sess.exists():
        return {
            "verdict": "ERROR",
            "is_blocking": True,
            "explanation": "No active .omp_wip session directory found."
        }

    iga_path = sess / "00_cartography" / "input_gap_analysis.md"
    cart_path = sess / "00_cartography" / "cartography_report.md"

    text_to_audit = ""
    if iga_path.exists():
        text_to_audit += "\n" + iga_path.read_text(encoding="utf-8")
    if cart_path.exists():
        text_to_audit += "\n" + cart_path.read_text(encoding="utf-8")

    if not text_to_audit.strip():
        return {
            "verdict": "BLOCKING_VETO",
            "is_blocking": True,
            "explanation": f"Cartography report and input gap analysis missing or empty under {sess / '00_cartography'}"
        }

    res = audit_specification_text(text_to_audit)
    res["session_path"] = str(sess)
    return res


def main():
    parser = argparse.ArgumentParser(description="Input Gap Analysis (IGA) & Plausibility Trap Auditor.")
    parser.add_argument("--spec-file", help="Path to specification markdown or text file")
    parser.add_argument("--text", help="Raw specification text to audit")
    parser.add_argument("--session-path", help="Path to .omp_wip session directory")
    parser.add_argument("--workspace-root", help="Root directory containing .omp_wip")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if args.spec_file:
        p = Path(args.spec_file).resolve()
        if not p.exists():
            print(f"[ERROR] Specification file not found: {p}", file=sys.stderr)
            sys.exit(1)
        text = p.read_text(encoding="utf-8")
        result = audit_specification_text(text)
    elif args.text:
        result = audit_specification_text(args.text)
    else:
        sess_dir = Path(args.session_path).resolve() if args.session_path else None
        result = audit_session_cartography(sess_dir, args.workspace_root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\033[36m==> Input Gap Analysis & Plausibility Trap Audit\033[0m")
        status_color = "\033[31m" if result.get("is_blocking") else "\033[32m"
        print(f"Verdict:              {status_color}{result.get('verdict')}\033[0m")
        print(f"Blocking Sev-1 Gaps:  {result.get('sev_1_count', 0)}")
        print(f"Ambiguous Sev-2 Gaps: {result.get('sev_2_count', 0)}")
        print(f"Authoritative Citations: {'YES' if result.get('has_authoritative_citations') else 'NO (Recommended: RFC/IEEE/Vendor docs)'}")
        print(f"Explanation:          {result.get('explanation')}")

        gaps = result.get("detected_gaps", [])
        if gaps:
            print("\n\033[33mIdentified Input Gaps:\033[0m")
            for idx, g in enumerate(gaps, 1):
                sev_color = "\033[31m" if g["severity"] == "Sev-1" else "\033[33m"
                print(f"  {idx}. [{sev_color}{g['severity']}\033[0m] {g['name']} ({g['category']})")
                print(f"     Description: {g['description']}")
                print(f"     Missing:     {', '.join(g['missing_invariants'])}")

    if result.get("is_blocking"):
        sys.exit(1)


if __name__ == "__main__":
    main()
