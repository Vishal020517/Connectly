"""
In-memory state store for active graph states.
Keyed by session_id — one entry per chat session.
This bridges the stateless HTTP layer with LangGraph's stateful graphs.
"""

from typing import Dict, Any

_candidate_states: Dict[str, Any] = {}
_recruiter_states: Dict[str, Any] = {}


def _session_key(user_id: str, session_id: str | None) -> str:
    return session_id or user_id


# --- Candidate ---

def get_candidate_state(user_id: str, session_id: str | None = None) -> dict:
    key = _session_key(user_id, session_id)
    if key not in _candidate_states:
        _candidate_states[key] = _default_candidate_state(user_id)
    return _candidate_states[key]


def set_candidate_state(user_id: str, state: dict, session_id: str | None = None):
    key = _session_key(user_id, session_id)
    _candidate_states[key] = state


def _default_candidate_state(user_id: str) -> dict:
    return {
        "user_query":          "",
        "user_id":             user_id,
        "profile_id":          None,
        "intent":              "",
        "confidence":          0.0,
        "reason":              "",
        "profile_data":        {},
        "extracted_profile":   {},
        "available_profiles":  None,
        "missing_fields":      [],
        "next_question":       None,
        "is_complete":         False,
        "stage":               None,
        "error":               None,
        "confirmation_message": None,
        "response":            "",
    }


# --- Recruiter ---

def get_recruiter_state(user_id: str, session_id: str | None = None) -> dict:
    key = _session_key(user_id, session_id)
    if key not in _recruiter_states:
        _recruiter_states[key] = _default_recruiter_state(user_id)
    return _recruiter_states[key]


def set_recruiter_state(user_id: str, state: dict, session_id: str | None = None):
    key = _session_key(user_id, session_id)
    _recruiter_states[key] = state


def _default_recruiter_state(user_id: str) -> dict:
    return {
        "user_query":    "",
        "user_id":       user_id,
        "job_id":        None,
        "intent":        "",
        "confidence":    0.0,
        "reason":        "",
        "job_data":      {},
        "extracted_job": {},
        "available_jobs": None,
        "missing_fields": [],
        "next_question":  None,
        "is_complete":    False,
        "stage":          None,
        "error":          None,
        "response":       "",
    }
