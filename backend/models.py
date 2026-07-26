from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_id: str          # chosen by user on the landing page
    message: str
    session_id: Optional[str] = None   # per-chat thread (defaults to user_id)
    profile_id: Optional[str] = None   # candidate: active profile
    job_id: Optional[str] = None       # recruiter: active job


class ChatResponse(BaseModel):
    reply: str            # what the AI says back
    user_id: str
    profile_id: Optional[str] = None
    job_id: Optional[str] = None
    intent: Optional[str] = None
    stage: Optional[str] = None
    available_profiles: Optional[list] = None
    available_jobs: Optional[list] = None
