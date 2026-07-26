from pydantic import BaseModel,Field
from typing import Literal

class RecruiterIntentOutputSchema(BaseModel):
    intent:Literal[
        "Create_job",
        "Update_job",
        "View_jobs",
        "Delete_job",
        "Search_candidates",
        "General_query"
    ]
    confidence:float=Field(..., ge=0.0, le=1.0)
    reason:str