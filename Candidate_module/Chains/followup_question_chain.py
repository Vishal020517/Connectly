from typing import List
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class FollowUpOutput(BaseModel):
    question:str

llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

parser=PydanticOutputParser(pydantic_object=FollowUpOutput)

followUp_prompt=ChatPromptTemplate.from_messages([
    ("system",
    """
    You are a conversational job profile assistant.

    The user is creating a job profile.

    Based on the missing fields, generate ONE short, clear follow-up question
    to collect the most important missing information.

    Rules:
    - Ask only one question.
    - Keep it under 20 words.
    - Be natural and conversational.
    - Do not mention field names directly.

    Example output:
    {{
    "question": "What is your notice period in days?"
    }}

    Return only valid JSON.

    """),
    ("human",
    """
    Missing fields:
    {missing_fields}

    Current profile data:
    {profile_data}
    """)
])

follow_up_chain=followUp_prompt|llm|parser

def generate_followup_question(missing_fields:List[str],profile_data:dict)->str:
    response=follow_up_chain.invoke({
        "missing_fields": missing_fields,
        "profile_data": profile_data
    })
    print("Follow-up Chain Response:", response)
    return response

if __name__ == "__main__":

    # Simulate missing fields after validation
    test_missing_fields = [
        "preferred_work_type",
        "notice_period_days"
    ]

    # Simulate already collected profile data
    test_profile_data = {
        "skills": ["React", "Node"],
        "total_experience_years": 3,
        "expected_salary_min": 15,
        "expected_salary_max": 20,
        "currency": "LPA"
    }

    result = generate_followup_question(
        missing_fields=test_missing_fields,
        profile_data=test_profile_data
    )

    print("Generated Question:")
    print(result.question)