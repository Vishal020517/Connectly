from Utils.job_to_text import job_to_text
from Utils.embedder import generate_embeddings
from Utils.candidate_fetcher import fetch_candidates_by_ids
from Utils.candidate_matcher import find_matching_candidates
from Recruiter_module.DB.job_store import collection as jobs_collection


def candidate_matching_node(state):
    job_data     = state.get("job_data")
    user_query   = state.get("user_query", "")
    recruiter_id = state.get("user_id")
    job_id       = state.get("job_id")

    # --- Resolve job_data ---
    # Priority 1: job_data already in state (recruiter just created/loaded a job this session)
    # Priority 2: load the specific job by job_id from MongoDB (recruiter mentions a job_id)
    # Priority 3: load the most recent job this recruiter posted from MongoDB
    # Priority 4: use the raw query text as the search signal (last resort)

    if not job_data:
        loaded_job = None

        if job_id and recruiter_id:
            # Load the specific job they're referring to
            loaded_job = jobs_collection.find_one(
                {"job_id": job_id, "recruiter_id": recruiter_id},
                {"_id": 0}
            )
            print(f"📂 Loaded job by job_id {job_id} from MongoDB")

        elif recruiter_id:
            # Load most recently created job for this recruiter
            loaded_job = jobs_collection.find_one(
                {"recruiter_id": recruiter_id},
                {"_id": 0},
                sort=[("created_at", -1)]
            )
            if loaded_job:
                print(f"📂 Auto-loaded most recent job '{loaded_job.get('role')}' from MongoDB")

        if loaded_job:
            job_data = loaded_job
        else:
            # Nothing in DB yet — fall back to raw query
            print("⚠️ No job found in DB — using raw query for candidate search")
            job_data = None

    if job_data:
        text = job_to_text(job_data)
    elif user_query:
        text = user_query
    else:
        return {
            **state,
            "response": "Please describe the role you are hiring for."
        }

    embedding   = generate_embeddings(text)
    results     = find_matching_candidates(embedding)
    profile_ids = results.get("ids", [])

    print("🔍 ChromaDB matched profile IDs:", profile_ids)

    if not profile_ids:
        return {
            **state,
            "response": "No matching candidates found."
        }

    candidates = fetch_candidates_by_ids(profile_ids)
    print("📦 MongoDB returned candidates:", len(candidates))

    if not candidates:
        return {
            **state,
            "response": "No matching candidates found."
        }

    # Update state with loaded job_data so subsequent searches reuse it
    response = "Top matching candidates:\n\n"

    for i, candidate in enumerate(candidates, 1):
        response += (
            f"{i}️⃣ Candidate ID: {candidate.get('user_id')}\n"
            f"💡 Skills: {', '.join(candidate.get('skills', []))}\n"
            f"📍 Location: {', '.join(candidate.get('preferred_locations', []))}\n"
            f"💼 Experience: {candidate.get('total_experience_years')} years\n\n"
            "--------------------------------------------------\n\n"
        )

    return {
        **state,
        "job_data":          job_data,   # persist loaded job back into state
        "matched_candidates": candidates,
        "response":          response
    }
