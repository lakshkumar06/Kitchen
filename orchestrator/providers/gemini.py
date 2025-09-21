# orchestrator/providers/gemini.py
"""
Gemini wrapper for the Manager agent.

ENV:
  GEMINI_API_KEY          # if using google-generativeai (API key mode)
  GEMINI_MODEL=gemini-1.5-flash  # optional override

Public funcs:
  get_idea_candidates(domain: str) -> list[str]
  plan_spec(idea: str | None, domain: str | None) -> dict | str
  fix_invalid_json(bad_text: str) -> str
"""

from __future__ import annotations
import os
import json
from typing import Any

# ✅ correct import
import google.generativeai as genai

# Import your prompts/helpers from agents.manager
from ..agents.manager import MANAGER_SYS, build_spec_prompt, build_ideas_prompt

from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"  # points to orchestrator/.env
load_dotenv(dotenv_path=str(ENV_PATH), override=False)

# ---------------------------------------------------------------------------

_API_KEY = os.getenv("GEMINI_API_KEY")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if _API_KEY:
    genai.configure(api_key=_API_KEY)
else:
    print("[gemini] Warning: GEMINI_API_KEY not set — using SAMPLE_SPEC fallback if needed.")

def _model(system_instruction: str | None = None):
    kwargs = {"model_name": _MODEL}
    if system_instruction:
        kwargs["system_instruction"] = system_instruction
    return genai.GenerativeModel(**kwargs)

def _parse_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None

# Minimal fallback so you can demo even if LLM fails
SAMPLE_SPEC: dict[str, Any] = {
    "app": {"name": "TaskTrack", "non_functional": ["pagination"]},
    "entities": [
        {
            "name": "Project",
            "fields": [
                {"name": "id", "type": "uuid", "primary": True},
                {"name": "name", "type": "string", "required": True},
                {"name": "created_at", "type": "datetime", "default": "now"},
            ],
            "relations": [],
        },
        {
            "name": "Task",
            "fields": [
                {"name": "id", "type": "uuid", "primary": True},
                {"name": "title", "type": "string", "required": True},
                {"name": "status", "type": "enum", "values": ["TODO", "DOING", "DONE"], "default": "TODO"},
                {"name": "project_id", "type": "uuid", "required": True},
            ],
            "relations": [{"type": "belongsTo", "target": "Project", "via": "project_id"}],
        },
    ],
    "pages": [
        {"path": "/", "type": "dashboard", "widgets": ["ProjectCount", "TasksByStatus"]},
        {"path": "/projects", "type": "list", "entity": "Project", "actions": ["create"]},
        {"path": "/tasks", "type": "list", "entity": "Task", "filters": ["status", "project_id"]},
    ],
    "api_conventions": {"base_path": "/api", "list_suffix": "s", "pagination": True},
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_idea_candidates(domain: str) -> list[str]:
    """Return EXACTLY 4 ideas for a domain as a list[str]."""
    default = ["Starter Dashboard", "CRUD Manager", "Notes & Tags", "Simple Tracker"]

    if not _API_KEY:
        return default

    resp = _model().generate_content(build_ideas_prompt(domain))
    text = (resp.text or "[]").strip()
    data = _parse_json(text)
    if isinstance(data, list) and data:
        return [str(x) for x in data[:4]]

    fixed = _parse_json(fix_invalid_json(text))
    if isinstance(fixed, list) and fixed:
        return [str(x) for x in fixed[:4]]

    return default


def plan_spec(idea: str | None, domain: str | None):
    """
    Turn a concrete idea into a normalized spec dict.
    If idea is None (user picked domain but not idea yet), return SAMPLE_SPEC so UI can proceed.
    """
    if not idea or not _API_KEY:
        return SAMPLE_SPEC

    resp = _model(MANAGER_SYS).generate_content(build_spec_prompt(idea))
    text = (resp.text or "").strip()

    data = _parse_json(text)
    if isinstance(data, dict):
        return data

    fixed_text = fix_invalid_json(text)
    fixed_data = _parse_json(fixed_text)
    if isinstance(fixed_data, dict):
        return fixed_data

    return SAMPLE_SPEC


def fix_invalid_json(bad_text: str) -> str:
    """Ask Gemini to make malformed JSON valid; returns a JSON string."""
    if not _API_KEY:
        return bad_text

    prompt = (
        "This should be valid JSON but isn't. "
        "Return strictly valid JSON only, no code fences, no commentary:\n"
        f"{bad_text}"
    )
    resp = _model().generate_content(prompt)
    return (resp.text or bad_text).strip()
