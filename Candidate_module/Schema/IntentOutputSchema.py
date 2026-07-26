from pydantic import BaseModel,Field
from typing import Literal

class IntentOutputSchema(BaseModel):
    intent:Literal[
        "create_profile",
        "update_profile",
        "delete_profile",
        "view_profile",
        "job_search",
        "resume_upload",
        "general_query"
    ]
    confidence:float = Field(..., ge=0.0, le=1.0)
    reason:str