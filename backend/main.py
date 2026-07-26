"""
WhisperNet API — FastAPI backend
Connects the LangGraph AI modules to the frontend via REST.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import candidate, recruiter, sidebar

app = FastAPI(title="WhisperNet API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5179", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])
app.include_router(recruiter.router, prefix="/recruiter", tags=["Recruiter"])
app.include_router(sidebar.router,   prefix="/sidebar",   tags=["Sidebar"])


@app.get("/health")
def health():
    return {"status": "ok"}
