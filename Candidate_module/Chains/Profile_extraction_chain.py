from typing import Optional,List
from pydantic import BaseModel,Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()



class PartialProfile(BaseModel):
    skills: Optional[List[str]] = None
    total_experience_years: Optional[float] = None
    preferred_work_type: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary_min: Optional[float] = None
    expected_salary_max: Optional[float] = None
    currency: Optional[str] = None
    notice_period_days: Optional[int] = None
    career_goals: Optional[str] = None

llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

parser=PydanticOutputParser(pydantic_object=PartialProfile)

profile_prompt=ChatPromptTemplate.from_messages([
    ("system",
     """
        You are a profile data extraction engine.

        Extract structured candidate profile information from the user message.

        Rules:
        - Only extract information explicitly mentioned.
        - Do NOT assume missing values.
        - If not mentioned, leave as null.
        - Be precise and structured.
        - You should extract the following fields if mentioned:
            - skills: List of skills (e.g. Python, React)
            - total_experience_years: Total years of experience (e.g. 3.5)
            - preferred_work_type: Preferred work type (e.g. remote, onsite, hybrid)
            - preferred_locations: List of preferred job locations (e.g. ["New York", "Remote"])
            - expected_salary_min: Minimum expected salary (e.g. 1500000)
            - expected_salary_max: Maximum expected salary (e.g. 2000000)
            - currency: Currency for salary expectations (e.g. USD, INR)
            - notice_period_days: Notice period in days (e.g. 30)
            - career_goals: Candidate's career goals or aspirations (e.g. "Looking to transition into a leadership role")

        Return only valid JSON.
     """
    ),
    ("human","{user_query}")
])

profile_extraction_chain=profile_prompt|llm|parser

def extract_profile_data(user_query:str)->PartialProfile:
    return profile_extraction_chain.invoke({
        "user_query": user_query
    })


if __name__ == "__main__":
    result = extract_profile_data(
        "I'm front end dev in React and Node. I prefer remote jobs in Chennai and expect 15 to 20 LPA"
    )
    print(result)