"""
Candidate seed script.

Drops all existing candidate_profiles documents, then inserts a fresh set
that matches the new schema (user_id + profile_id + all required fields).

Each candidate gets:
  - a stable user_id  (seed_candidate_<n>)
  - a stable profile_id (seed_profile_<n>)

Run with:
    python -m Candidate_module.seed_profile_data
"""

import uuid
from datetime import datetime

from Candidate_module.DB.mongo import collection
from Utils.profile_to_text import profile_to_text
from Utils.embedder import generate_embeddings
from Utils.vector_store import store_embedding

# ---------------------------------------------------------------------------
# Seed data — every required field is present so completeness = 1.0
# ---------------------------------------------------------------------------
CANDIDATE_PROFILES = [
    {
        "name": "Arjun Mehta",
        "skills": ["Python", "Django", "PostgreSQL"],
        "total_experience_years": 3,
        "preferred_work_type": "remote",
        "preferred_locations": ["Bangalore"],
        "expected_salary_min": 1200000,
        "expected_salary_max": 1600000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a senior backend engineer",
    },
    {
        "name": "Priya Sharma",
        "skills": ["React", "TypeScript", "Next.js"],
        "total_experience_years": 2.5,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Hyderabad"],
        "expected_salary_min": 900000,
        "expected_salary_max": 1200000,
        "currency": "INR",
        "notice_period_days": 45,
        "career_goals": "Grow into a frontend architect role",
    },
    {
        "name": "Rohit Nair",
        "skills": ["Java", "Spring Boot", "Microservices"],
        "total_experience_years": 4,
        "preferred_work_type": "onsite",
        "preferred_locations": ["Pune"],
        "expected_salary_min": 1400000,
        "expected_salary_max": 1800000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Lead backend platform projects",
    },
    {
        "name": "Sneha Iyer",
        "skills": ["SQL", "Power BI", "Excel"],
        "total_experience_years": 2,
        "preferred_work_type": "remote",
        "preferred_locations": ["Chennai", "Remote"],
        "expected_salary_min": 700000,
        "expected_salary_max": 950000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a data analytics specialist",
    },
    {
        "name": "Vikram Rao",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform"],
        "total_experience_years": 5,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Mumbai"],
        "expected_salary_min": 1800000,
        "expected_salary_max": 2400000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Become a cloud solutions architect",
    },
    {
        "name": "Ananya Krishnan",
        "skills": ["Flutter", "Dart", "Firebase"],
        "total_experience_years": 3,
        "preferred_work_type": "remote",
        "preferred_locations": ["Kochi", "Remote"],
        "expected_salary_min": 1000000,
        "expected_salary_max": 1400000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Build scalable mobile products",
    },
    {
        "name": "Karan Verma",
        "skills": ["Node.js", "Express", "MongoDB", "Redis"],
        "total_experience_years": 4.5,
        "preferred_work_type": "onsite",
        "preferred_locations": ["Gurugram"],
        "expected_salary_min": 1500000,
        "expected_salary_max": 2000000,
        "currency": "INR",
        "notice_period_days": 45,
        "career_goals": "Move into engineering management",
    },
    {
        "name": "Divya Pillai",
        "skills": ["Selenium", "Cypress", "API Testing"],
        "total_experience_years": 3,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Noida"],
        "expected_salary_min": 900000,
        "expected_salary_max": 1250000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a QA automation lead",
    },
    {
        "name": "Aditya Joshi",
        "skills": ["C#", ".NET Core", "Azure"],
        "total_experience_years": 6,
        "preferred_work_type": "remote",
        "preferred_locations": ["Bengaluru"],
        "expected_salary_min": 2000000,
        "expected_salary_max": 2800000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Become a principal engineer",
    },
    {
        "name": "Meera Nambiar",
        "skills": ["Go", "Kafka", "Distributed Systems"],
        "total_experience_years": 5,
        "preferred_work_type": "onsite",
        "preferred_locations": ["Chennai"],
        "expected_salary_min": 1700000,
        "expected_salary_max": 2300000,
        "currency": "INR",
        "notice_period_days": 90,
        "career_goals": "Design high scale backend systems",
    },
    {
        "name": "Rishi Gupta",
        "skills": ["Figma", "Adobe XD", "Design Systems"],
        "total_experience_years": 2.8,
        "preferred_work_type": "remote",
        "preferred_locations": ["Delhi", "Remote"],
        "expected_salary_min": 850000,
        "expected_salary_max": 1150000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a senior product designer",
    },
    {
        "name": "Tanvi Desai",
        "skills": ["Machine Learning", "PyTorch", "NLP"],
        "total_experience_years": 4,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Bangalore"],
        "expected_salary_min": 1900000,
        "expected_salary_max": 2600000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Become an AI research engineer",
    },
    {
        "name": "Nikhil Bhat",
        "skills": ["Android", "Kotlin", "Jetpack Compose"],
        "total_experience_years": 3.2,
        "preferred_work_type": "onsite",
        "preferred_locations": ["Hyderabad"],
        "expected_salary_min": 1100000,
        "expected_salary_max": 1500000,
        "currency": "INR",
        "notice_period_days": 45,
        "career_goals": "Lead mobile app architecture",
    },
    {
        "name": "Pooja Shetty",
        "skills": ["Salesforce Apex", "LWC", "Integrations"],
        "total_experience_years": 4,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Pune"],
        "expected_salary_min": 1400000,
        "expected_salary_max": 1900000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Become a Salesforce technical consultant",
    },
    {
        "name": "Sameer Kulkarni",
        "skills": ["Network Security", "SIEM", "Incident Response"],
        "total_experience_years": 5,
        "preferred_work_type": "onsite",
        "preferred_locations": ["Kolkata"],
        "expected_salary_min": 1600000,
        "expected_salary_max": 2200000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a cybersecurity manager",
    },
    {
        "name": "Ishaan Tiwari",
        "skills": ["Rust", "Systems Programming", "Linux Internals"],
        "total_experience_years": 4,
        "preferred_work_type": "remote",
        "preferred_locations": ["Remote", "Bengaluru"],
        "expected_salary_min": 1800000,
        "expected_salary_max": 2500000,
        "currency": "INR",
        "notice_period_days": 45,
        "career_goals": "Build performance critical infrastructure",
    },
    {
        "name": "Kavya Reddy",
        "skills": ["Business Analysis", "SQL", "Stakeholder Management"],
        "total_experience_years": 3,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Ahmedabad"],
        "expected_salary_min": 950000,
        "expected_salary_max": 1300000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a product strategy lead",
    },
    {
        "name": "Yash Patel",
        "skills": ["React Native", "JavaScript", "REST APIs"],
        "total_experience_years": 2,
        "preferred_work_type": "remote",
        "preferred_locations": ["Jaipur", "Remote"],
        "expected_salary_min": 800000,
        "expected_salary_max": 1100000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Become a cross platform mobile expert",
    },
    {
        "name": "Neha Saxena",
        "skills": ["Data Engineering", "Spark", "Airflow"],
        "total_experience_years": 5.5,
        "preferred_work_type": "hybrid",
        "preferred_locations": ["Mumbai"],
        "expected_salary_min": 2000000,
        "expected_salary_max": 2700000,
        "currency": "INR",
        "notice_period_days": 60,
        "career_goals": "Become a data platform architect",
    },
    {
        "name": "Rahul Nair",
        "skills": ["Technical Writing", "API Documentation", "Developer Education"],
        "total_experience_years": 3,
        "preferred_work_type": "remote",
        "preferred_locations": ["Chennai"],
        "expected_salary_min": 900000,
        "expected_salary_max": 1250000,
        "currency": "INR",
        "notice_period_days": 30,
        "career_goals": "Lead developer documentation initiatives",
    },
]

REQUIRED_FIELDS = [
    "skills", "total_experience_years", "expected_salary_min",
    "expected_salary_max", "preferred_locations", "preferred_work_type",
    "notice_period_days", "career_goals", "currency",
]


def seed_candidate_profiles() -> None:
    # -----------------------------------------------------------------------
    # Step 1: Wipe only previously seeded profiles (not real user profiles)
    # -----------------------------------------------------------------------
    deleted = collection.delete_many({"extracted_from": "seed"})
    print(f"🗑️  Deleted {deleted.deleted_count} existing seed profile(s).\n")

    # -----------------------------------------------------------------------
    # Step 2: Insert fresh profiles with profile_id + user_id
    # -----------------------------------------------------------------------
    for idx, profile in enumerate(CANDIDATE_PROFILES, start=1):
        user_id    = f"seed_candidate_{idx}"
        profile_id = f"seed_profile_{idx}"

        filled = sum(1 for f in REQUIRED_FIELDS if profile.get(f) not in [None, "", []])
        completeness = filled / len(REQUIRED_FIELDS)

        document = {
            "user_id":             user_id,
            "profile_id":          profile_id,
            **profile,
            "profile_completeness": completeness,
            "extracted_from":      "seed",
            "created_at":          datetime.utcnow(),
            "updated_at":          datetime.utcnow(),
        }

        collection.insert_one(document)

        # Store embedding so the candidate is discoverable by recruiters
        text       = profile_to_text(profile)
        embeddings = generate_embeddings(text)
        store_embedding(profile_id, embeddings, text)   # keyed by profile_id

        print(f"✅ [{idx:02d}] {profile['name']}  |  user_id: {user_id}  |  profile_id: {profile_id}")

    print(f"\n🎉 Seeded {len(CANDIDATE_PROFILES)} candidate profiles successfully.")


if __name__ == "__main__":
    seed_candidate_profiles()
