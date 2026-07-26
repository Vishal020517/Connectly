"""
Sidebar data endpoints — profiles for candidates, jobs for recruiters.
These power the sidebar panel in the UI.
"""

from fastapi import APIRouter
from typing import List, Dict, Any

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from Candidate_module.DB.mongo import collection as profiles_col
from Recruiter_module.DB.job_store import collection as jobs_col

router = APIRouter()


@router.get("/profiles/{user_id}", response_model=List[Dict[str, Any]])
def get_profiles(user_id: str):
    """Return all profiles for a candidate, with a short display ID."""
    docs = list(profiles_col.find({"user_id": user_id}, {"_id": 0}))
    result = []
    for doc in docs:
        pid = doc.get("profile_id", "")
        result.append({
            "profile_id":   pid,
            "short_id":     pid[:8] if pid else "—",   # first 8 chars for display
            "skills":       doc.get("skills", []),
            "role_hint":    ", ".join(doc.get("skills", [])[:2]),
            "completeness": round(doc.get("profile_completeness", 0) * 100),
            "work_type":    doc.get("preferred_work_type", ""),
            "locations":    doc.get("preferred_locations", []),
            "experience":   doc.get("total_experience_years", ""),
        })
    return result


@router.get("/jobs/{user_id}", response_model=List[Dict[str, Any]])
def get_jobs(user_id: str):
    """Return all jobs posted by a recruiter, with a short display ID."""
    docs = list(jobs_col.find({"recruiter_id": user_id}, {"_id": 0}))
    result = []
    for doc in docs:
        jid = doc.get("job_id", "")
        result.append({
            "job_id":      jid,
            "short_id":    jid[:8] if jid else "—",
            "role":        doc.get("role", ""),
            "company":     doc.get("company_name", ""),
            "location":    doc.get("location", ""),
            "experience":  doc.get("experience", ""),
            "skills":      doc.get("skills", []),
        })
    return result
