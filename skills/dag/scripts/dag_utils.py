#!/usr/bin/env python3
"""
dag_utils.py - Unified Resource Resolution and Helper Utilities for F-DAG Engine.
Zero hardcoded user paths. Resolves assets dynamically from skill directory structure.
"""

from pathlib import Path
from typing import Optional, List
import json
import os
import re

ENGINE_DIR = Path(__file__).parent.resolve()
SKILL_DIR = ENGINE_DIR.parent.resolve()
TEMPLATES_DIR = SKILL_DIR / "resources" / "templates"
PERSONAS_DIR = SKILL_DIR / "resources" / "personas"


def get_engine_dir() -> Path:
    return ENGINE_DIR


def get_skill_dir() -> Path:
    return SKILL_DIR


def get_templates_dir() -> Path:
    return TEMPLATES_DIR


def get_personas_dir() -> Path:
    return PERSONAS_DIR


def find_latest_session(workspace_root: Optional[str] = None) -> Optional[Path]:
    """Locates the latest active .omp_wip session directory."""
    search_root = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
    for parent in [search_root] + list(search_root.parents):
        wip_dir = parent / ".omp_wip"
        if wip_dir.is_dir():
            sessions = [d for d in wip_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if sessions:
                sessions.sort(key=lambda x: x.name, reverse=True)
                return sessions[0]
    return None


def find_resource_file(filename: str, session_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Dynamically finds a resource file (schema, template, persona) across:
    1. session_dir or its ancestor .omp_wip directory
    2. resources/templates/
    3. resources/personas/
    4. scripts/
    5. current working directory
    """
    candidates: List[Path] = []
    if session_dir:
        candidates.append(session_dir / filename)
        candidates.append(session_dir.parent / filename)
        candidates.append(session_dir.parent.parent / filename)

    candidates.extend([
        TEMPLATES_DIR / filename,
        PERSONAS_DIR / filename,
        ENGINE_DIR / filename,
        Path.cwd() / filename,
    ])

    for cand in candidates:
        if cand.exists():
            return cand.resolve()
    return None
