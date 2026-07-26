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
    "question": "Which company do you need this requirement?"
    }}

    Return only valid JSON.

    """),
    ("human",
    """
    Missing fields:
    {missing_fields}

    Current job data:
    {job_data}
    """)
])

follow_up_chain=followUp_prompt|llm|parser

def generate_followup_question(missing_fields:List[str],job_data):
    return follow_up_chain.invoke({
        "missing_fields": missing_fields,
        "job_data": job_data
    })

if __name__ == "__main__":
    result = generate_followup_question(
        ["skills", "experience"],
        {"role": "Frontend Developer"}
    )

    print(result)
