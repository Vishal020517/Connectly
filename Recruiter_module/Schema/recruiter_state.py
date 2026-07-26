from typing import TypedDict, Optional, List, Dict, Any, Annotated


class RecruiterState(TypedDict):
    user_query: str

    # user_id is the recruiter's identity.
    # It doubles as recruiter_id — stored on every job document so we
    # can always filter "jobs owned by this recruiter" with a single field.
    user_id: str

    # job_id holds the currently selected job (set after listing/saving).
    # Update and delete nodes use this for precise, single-job targeting.
    job_id: Optional[str]

    intent: str
    confidence: float
    reason: str

    job_data: Annotated[dict, "persist"]
    extracted_job: dict

    # populated by view_jobs_node so the recruiter can pick a specific job
    # by index or job_id without re-querying the DB.
    available_jobs: Optional[List[Dict[str, Any]]]

    missing_fields: List[str]
    next_question: Optional[str]

    is_complete: Optional[bool]
    stage: Optional[str]
    error: Optional[str]

    response: str
