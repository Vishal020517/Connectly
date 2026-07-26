from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os
from dotenv import load_dotenv
from Recruiter_module.Schema.job_extraction_schema import JobExtractionSchema

load_dotenv()

llm=ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

parser=PydanticOutputParser(pydantic_object=JobExtractionSchema)

job_profile_prompt=ChatPromptTemplate.from_messages(
    [
        ("system", """
        You are an AI recruiter assistant.

        Your task is to extract job-related information from the user input.

        Extract the following fields:
        - company_name 
        - apply_link
        - role
        - skills (list)
        - experience
        - location
        - job_description
       

        Rules:
        - If a field is not present, leave it empty
        - Identify missing fields and add them to "missing_fields"
        - Skills should always be a list
        - Do NOT hallucinate values
         
        IMPORTANT RULES:
        - Extract role even if phrased like:
        - "delete the role of Data Analyst"
        - "update AI Engineer job"
        - "remove frontend developer"
        - Always identify the job role clearly
        - Do not leave role empty if it is mentioned in any form

        Return ONLY valid JSON
        """),

        ("human", "{user_input}")
    ]
)

job_extraction_chain=job_profile_prompt|llm|parser

def extract_job_entities(user_input:str)->JobExtractionSchema:
    return job_extraction_chain.invoke({"user_input": user_input})

if __name__=="__main__":
    while True:
        user_input = input("Recruiter: ")

        result = extract_job_entities(user_input)

        print("\nExtracted Data:")
        print(result)
        print("-" * 50)