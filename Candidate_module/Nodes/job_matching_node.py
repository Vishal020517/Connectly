from Utils.profile_to_text import profile_to_text
from Utils.embedder import generate_embeddings
from Utils.job_matcher import find_matching_jobs
from Utils.job_fetcher import fetch_jobs_by_ids
from Candidate_module.DB.mongo import collection


def job_matching_node(state):
    profile_data = state.get("profile_data")
    user_id      = state.get("user_id")
    profile_id   = state.get("profile_id")

    # --- Load profile from MongoDB if not in state (e.g. after a restart) ---
    if not profile_data:
        loaded = None

        if profile_id and user_id:
            # Load the specific profile they were working with
            loaded = collection.find_one(
                {"profile_id": profile_id, "user_id": user_id},
                {"_id": 0}
            )
            print(f"📂 Loaded profile by profile_id {profile_id} from MongoDB")

        elif user_id:
            # Load the most recently updated profile for this user
            loaded = collection.find_one(
                {"user_id": user_id},
                {"_id": 0},
                sort=[("updated_at", -1)]
            )
            if loaded:
                print(f"📂 Auto-loaded most recent profile for user {user_id} from MongoDB")

        if loaded:
            profile_data = {
                k: v for k, v in loaded.items()
                if k not in ["_id", "created_at", "updated_at"]
            }
            profile_id = loaded.get("profile_id")
        else:
            return {
                **state,
                "response": "Please create a profile first so I can find matching jobs for you."
            }

    text       = profile_to_text(profile_data)
    embeddings = generate_embeddings(text)
    results    = find_matching_jobs(embeddings)
    job_ids    = results.get("ids", [])

    print("🔍 ChromaDB matched job IDs:", job_ids)

    if not job_ids:
        return {
            **state,
            "response": "No matching jobs found."
        }

    jobs = fetch_jobs_by_ids(job_ids)

    if not jobs:
        return {
            **state,
            "response": "No matching jobs found."
        }

    response = "Top matching jobs:\n\n"

    for i, job in enumerate(jobs, 1):
        response += (
            f"{i}️⃣ {job.get('role')} at {job.get('company_name')}\n"
            f"📍 Location: {job.get('location')}\n"
            f"💼 Experience: {job.get('experience')}\n"
            f"🔗 Apply: {job.get('apply_link')}\n\n"
            "--------------------------------------------------\n\n"
        )

    return {
        **state,
        "profile_data": profile_data,   # persist back so next search reuses it
        "profile_id":   profile_id,
        "matched_jobs": jobs,
        "response":     response
    }
