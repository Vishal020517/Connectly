"""
Recruiter seed script.

Drops all existing jobs documents, then inserts a fresh set that matches
the new schema (recruiter_id + job_id + all required fields).

Jobs are distributed across 4 seed recruiters so the ownership isolation
can be tested immediately:
  - seed_recruiter_1  →  jobs 1-6
  - seed_recruiter_2  →  jobs 7-12
  - seed_recruiter_3  →  jobs 13-18
  - seed_recruiter_4  →  jobs 19-24

Run with:
    python -m Recruiter_module.seed_job_data
"""

import uuid
from datetime import datetime

from Recruiter_module.DB.job_store import collection
from Utils.job_to_text import job_to_text
from Utils.embedder import generate_embeddings
from Utils.vector_store import store_job_embedding

# ---------------------------------------------------------------------------
# Seed data — all required fields present
# ---------------------------------------------------------------------------
JOB_POSTS = [
    # --- seed_recruiter_1 (Nimbus Labs, PixelForge, InsightWave, CloudArc, NeuralNest, TestSphere) ---
    {
        "company_name": "Nimbus Labs",
        "role": "Backend Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience": "3+ years",
        "location": "Bangalore",
        "apply_link": "https://nimbus.example.com/jobs/backend-dev",
    },
    {
        "company_name": "PixelForge",
        "role": "Frontend Engineer",
        "skills": ["React", "TypeScript", "Redux"],
        "experience": "2-4 years",
        "location": "Hyderabad",
        "apply_link": "https://pixelforge.example.com/careers/frontend-engineer",
    },
    {
        "company_name": "InsightWave",
        "role": "Data Analyst",
        "skills": ["SQL", "Excel", "Power BI"],
        "experience": "1-3 years",
        "location": "Pune",
        "apply_link": "https://insightwave.example.com/jobs/data-analyst",
    },
    {
        "company_name": "CloudArc",
        "role": "DevOps Engineer",
        "skills": ["AWS", "Docker", "Kubernetes", "CI/CD"],
        "experience": "4+ years",
        "location": "Chennai",
        "apply_link": "https://cloudarc.example.com/jobs/devops",
    },
    {
        "company_name": "NeuralNest",
        "role": "Machine Learning Engineer",
        "skills": ["Python", "PyTorch", "NLP"],
        "experience": "3+ years",
        "location": "Mumbai",
        "apply_link": "https://neuralnest.example.com/jobs/ml-engineer",
    },
    {
        "company_name": "TestSphere",
        "role": "QA Automation Engineer",
        "skills": ["Selenium", "Python", "API Testing"],
        "experience": "2-5 years",
        "location": "Noida",
        "apply_link": "https://testsphere.example.com/careers/qa-automation",
    },

    # --- seed_recruiter_2 (AppTrail, CodeHarbor, VisionLoop, PixelMint, ShieldGrid, StreamForge) ---
    {
        "company_name": "AppTrail",
        "role": "Mobile App Developer",
        "skills": ["Flutter", "Dart", "Firebase"],
        "experience": "2+ years",
        "location": "Kochi",
        "apply_link": "https://apptrail.example.com/jobs/flutter-dev",
    },
    {
        "company_name": "CodeHarbor",
        "role": "Full Stack Developer",
        "skills": ["Node.js", "React", "MongoDB"],
        "experience": "3-6 years",
        "location": "Gurugram",
        "apply_link": "https://codeharbor.example.com/jobs/fullstack",
    },
    {
        "company_name": "VisionLoop",
        "role": "Product Manager",
        "skills": ["Roadmap Planning", "Analytics", "Stakeholder Communication"],
        "experience": "5+ years",
        "location": "Bangalore",
        "apply_link": "https://visionloop.example.com/jobs/product-manager",
    },
    {
        "company_name": "PixelMint",
        "role": "UI UX Designer",
        "skills": ["Figma", "Prototyping", "Design Systems"],
        "experience": "2-4 years",
        "location": "Pune",
        "apply_link": "https://pixelmint.example.com/careers/ui-ux-designer",
    },
    {
        "company_name": "ShieldGrid",
        "role": "Cybersecurity Analyst",
        "skills": ["SIEM", "Incident Response", "Network Security"],
        "experience": "3+ years",
        "location": "Hyderabad",
        "apply_link": "https://shieldgrid.example.com/jobs/security-analyst",
    },
    {
        "company_name": "StreamForge",
        "role": "Data Engineer",
        "skills": ["Spark", "Kafka", "Airflow"],
        "experience": "4+ years",
        "location": "Chennai",
        "apply_link": "https://streamforge.example.com/jobs/data-engineer",
    },

    # --- seed_recruiter_3 (UptimeCore, MarketPulse, DocSprint, SkyRoute, CRMStack, LedgerFlow) ---
    {
        "company_name": "UptimeCore",
        "role": "Site Reliability Engineer",
        "skills": ["Linux", "Kubernetes", "Monitoring"],
        "experience": "4+ years",
        "location": "Bangalore",
        "apply_link": "https://uptimecore.example.com/jobs/sre",
    },
    {
        "company_name": "MarketPulse",
        "role": "Business Analyst",
        "skills": ["SQL", "Reporting", "Requirement Gathering"],
        "experience": "2-5 years",
        "location": "Delhi",
        "apply_link": "https://marketpulse.example.com/jobs/business-analyst",
    },
    {
        "company_name": "DocSprint",
        "role": "Technical Writer",
        "skills": ["API Documentation", "Developer Docs"],
        "experience": "2+ years",
        "location": "Remote",
        "apply_link": "https://docsprint.example.com/jobs/technical-writer",
    },
    {
        "company_name": "SkyRoute",
        "role": "Cloud Engineer",
        "skills": ["AWS", "Terraform", "Networking"],
        "experience": "3+ years",
        "location": "Mumbai",
        "apply_link": "https://skyroute.example.com/jobs/cloud-engineer",
    },
    {
        "company_name": "CRMStack",
        "role": "Salesforce Developer",
        "skills": ["Apex", "Lightning Web Components", "Integrations"],
        "experience": "3-5 years",
        "location": "Pune",
        "apply_link": "https://crmstack.example.com/jobs/salesforce-developer",
    },
    {
        "company_name": "LedgerFlow",
        "role": "Blockchain Developer",
        "skills": ["Solidity", "Smart Contracts", "Web3"],
        "experience": "2-4 years",
        "location": "Bengaluru",
        "apply_link": "https://ledgerflow.example.com/jobs/blockchain-dev",
    },

    # --- seed_recruiter_4 (PixelRaid, PromptWorks, BizFlow, NetBridge, HelpOrbit, PeopleSync) ---
    {
        "company_name": "PixelRaid",
        "role": "Game Developer",
        "skills": ["Unity", "C#", "Gameplay Systems"],
        "experience": "2+ years",
        "location": "Hyderabad",
        "apply_link": "https://pixelraid.example.com/jobs/game-developer",
    },
    {
        "company_name": "PromptWorks",
        "role": "AI Prompt Engineer",
        "skills": ["Prompt Design", "Evaluation", "Python"],
        "experience": "1-3 years",
        "location": "Remote",
        "apply_link": "https://promptworks.example.com/jobs/prompt-engineer",
    },
    {
        "company_name": "BizFlow",
        "role": "ERP Consultant",
        "skills": ["ERP Implementation", "Process Mapping"],
        "experience": "4+ years",
        "location": "Ahmedabad",
        "apply_link": "https://bizflow.example.com/jobs/erp-consultant",
    },
    {
        "company_name": "NetBridge",
        "role": "Network Engineer",
        "skills": ["Routing", "Switching", "Firewall Management"],
        "experience": "3+ years",
        "location": "Kolkata",
        "apply_link": "https://netbridge.example.com/careers/network-engineer",
    },
    {
        "company_name": "HelpOrbit",
        "role": "Support Engineer",
        "skills": ["Troubleshooting", "Ticketing Tools", "SQL"],
        "experience": "1-3 years",
        "location": "Jaipur",
        "apply_link": "https://helporbit.example.com/jobs/support-engineer",
    },
    {
        "company_name": "PeopleSync",
        "role": "HR Tech Specialist",
        "skills": ["ATS Platforms", "HR Analytics", "Automation"],
        "experience": "3+ years",
        "location": "Chennai",
        "apply_link": "https://peoplesync.example.com/jobs/hr-tech-specialist",
    },
]

# Maps job index (1-based) to recruiter
def _recruiter_for(idx: int) -> str:
    if idx <= 6:
        return "seed_recruiter_1"
    elif idx <= 12:
        return "seed_recruiter_2"
    elif idx <= 18:
        return "seed_recruiter_3"
    else:
        return "seed_recruiter_4"


def seed_recruiter_job_data() -> None:
    # -----------------------------------------------------------------------
    # Step 1: Wipe only previously seeded jobs (not real recruiter jobs)
    # -----------------------------------------------------------------------
    deleted = collection.delete_many({"recruiter_id": {"$regex": "^seed_recruiter_"}})
    print(f"🗑️  Deleted {deleted.deleted_count} existing seed job(s).\n")

    # -----------------------------------------------------------------------
    # Step 2: Insert fresh jobs with recruiter_id + job_id
    # -----------------------------------------------------------------------
    for idx, job in enumerate(JOB_POSTS, start=1):
        job_id       = f"seed_job_{idx}"
        recruiter_id = _recruiter_for(idx)

        document = {
            "job_id":       job_id,
            "recruiter_id": recruiter_id,   # ownership anchor
            **job,
            "created_at":   datetime.utcnow(),
            "updated_at":   datetime.utcnow(),
        }

        collection.insert_one(document)

        # Store embedding so candidates can match against this job
        text       = job_to_text(job)
        embeddings = generate_embeddings(text)
        store_job_embedding(job_id, embeddings, text)

        print(
            f"✅ [{idx:02d}] {job['role']} @ {job['company_name']}"
            f"  |  job_id: {job_id}"
            f"  |  recruiter_id: {recruiter_id}"
        )

    print(f"\n🎉 Seeded {len(JOB_POSTS)} jobs across 4 recruiters successfully.")
    print("\nRecruiter summary:")
    print("  seed_recruiter_1  →  jobs 1-6   (Nimbus Labs, PixelForge, InsightWave, CloudArc, NeuralNest, TestSphere)")
    print("  seed_recruiter_2  →  jobs 7-12  (AppTrail, CodeHarbor, VisionLoop, PixelMint, ShieldGrid, StreamForge)")
    print("  seed_recruiter_3  →  jobs 13-18 (UptimeCore, MarketPulse, DocSprint, SkyRoute, CRMStack, LedgerFlow)")
    print("  seed_recruiter_4  →  jobs 19-24 (PixelRaid, PromptWorks, BizFlow, NetBridge, HelpOrbit, PeopleSync)")


if __name__ == "__main__":
    seed_recruiter_job_data()
