from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv
from Recruiter_module.Schema.recruiter_intent_schema import RecruiterIntentOutputSchema
from Recruiter_module.Schema.recruiter_state import RecruiterState
load_dotenv()

llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

parser=PydanticOutputParser(pydantic_object=RecruiterIntentOutputSchema)

intent_prompt=ChatPromptTemplate.from_messages(
    [
        ("system", """
        You are an intent classifier for a recruiter assistant.

        Classify the user's intent into EXACTLY one of the following:

        - Create_job → user wants to create or post a job
        - Update_job → user wants to modify a job
        - Delete_job → user wants to remove a job
        - View_jobs → user wants to see jobs
        - Search_candidates → user wants candidates
        - General_query → anything else

        IMPORTANT:
        - "create job", "post job", "create job post", "hire", "need a developer" → Create_job
        - "show jobs", "my jobs" → View_jobs
        - "delete job", "remove job" → Delete_job
        - "update job", "change job" → Update_job

        Return ONLY JSON:
        {{
        "intent": "",
        "confidence": 0.0,
        "reason": ""
        }}
        """),
        (
            "human","{user_query}"
        )
    ],
)

intent_chain=intent_prompt|llm|parser

def classify_recruiter_intent(user_query:str)->RecruiterState:
    return intent_chain.invoke({"user_query":user_query})

if __name__=="__main__":
    user_query="I need to post an job with the for a opening in my company with skills like react and node"
    result=classify_recruiter_intent(user_query)
    print(result)