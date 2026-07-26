from pydantic import BaseModel,Field
from typing import List

class JobExtractionSchema(BaseModel):
    company_name:str=""
    apply_link:str=""
    role: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: str = ""
    location: str = ""
    job_description: str = ""
    missing_fields: List[str] = Field(default_factory=list)