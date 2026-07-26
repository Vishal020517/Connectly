from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
You are an expert HR assistant.

Generate a professional job description based on given details.

Include:
- Role summary
- Required skills
- Experience
- Responsibilities
- Preferred qualifications

Keep it concise and professional.
"""),
        ("human", """
Role: {role}
Skills: {skills}
Experience: {experience}
Location: {location}
Company: {company_name}
""")
    ]
)

job_description_chain = prompt | llm


def generate_job_description(job_data: dict) -> str:
    response = job_description_chain.invoke({
        "role": job_data.get("role", ""),
        "skills": ", ".join(job_data.get("skills", [])),
        "experience": job_data.get("experience", ""),
        "location": job_data.get("location", ""),
        "company_name": job_data.get("company_name", "")
    })

    return response.content