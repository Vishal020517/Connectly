from Recruiter_module.DB.job_store import collection
from Recruiter_module.Chains.job_extraction_chain import extract_job_entities
from datetime import datetime


def update_job_node(state):
    recruiter_id = state.get("user_id")
    job_id       = state.get("job_id")
    stage        = state.get("stage")
    user_query   = state.get("user_query", "")

    if not recruiter_id:
        return {**state, "response": "Could not identify your account."}

    # --- update_pending_extract: user replied with actual changes ---
    if stage == "update_pending_extract":
        if not job_id:
            return {**state, "response": "No job selected. Please view your jobs first."}

        existing = collection.find_one(
            {"job_id": job_id, "recruiter_id": recruiter_id}
        )
        if not existing:
            return {**state, "stage": None, "response": "Job not found in your postings."}

        extracted = extract_job_entities(user_query).model_dump()
        updates   = {
            k: v for k, v in extracted.items()
            if v not in [None, "", []] and k != "missing_fields"
        }

        if not updates:
            return {**state, "stage": None, "response": "No valid updates found in your message."}

        updates["updated_at"] = datetime.utcnow()
        collection.update_one({"_id": existing["_id"]}, {"$set": updates})

        # Refresh job_data in state with the updated values
        updated_job = {**{k: v for k, v in existing.items() if k != "_id"}, **updates}

        return {
            **state,
            "job_data": updated_job,
            "stage":    None,
            "response": f"✅ '{existing.get('role')}' updated successfully."
        }

    # --- job_id in state + specific update in query — go straight to update ---
    if job_id and len(user_query.split()) > 5:
        existing = collection.find_one(
            {"job_id": job_id, "recruiter_id": recruiter_id}
        )
        if existing:
            extracted = extract_job_entities(user_query).model_dump()
            updates   = {
                k: v for k, v in extracted.items()
                if v not in [None, "", []] and k != "missing_fields"
            }
            if updates:
                updates["updated_at"] = datetime.utcnow()
                collection.update_one({"_id": existing["_id"]}, {"$set": updates})
                updated_job = {**{k: v for k, v in existing.items() if k != "_id"}, **updates}
                return {
                    **state,
                    "job_data": updated_job,
                    "stage":    None,
                    "response": f"✅ '{existing.get('role')}' updated successfully."
                }

    # --- No job_id or vague update — load job and ask what to change ---
    if job_id:
        existing = collection.find_one(
            {"job_id": job_id, "recruiter_id": recruiter_id}, {"_id": 0}
        )
        if existing:
            return _ask_what_to_update(state, existing)

    # Try to find by role extracted from query
    extracted = extract_job_entities(user_query).model_dump()
    role      = extracted.get("role", "")
    if role:
        existing = collection.find_one(
            {"role": role, "recruiter_id": recruiter_id}, {"_id": 0}
        )
        if existing:
            return _ask_what_to_update(state, existing)

    # Multiple jobs — ask which one to update
    jobs = list(collection.find({"recruiter_id": recruiter_id}, {"_id": 0}))

    if not jobs:
        return {**state, "response": "You have no job postings to update."}

    if len(jobs) == 1:
        return _ask_what_to_update(state, jobs[0])

    job_list = "\n".join(
        f"{i+1}. {j.get('role')} at {j.get('company_name')}  |  job_id: {j.get('job_id')}"
        for i, j in enumerate(jobs)
    )

    return {
        **state,
        "available_jobs": jobs,
        "stage":          "update_job_select",
        "response": (
            f"Which job would you like to update?\n\n{job_list}\n\n"
            "Reply with the job number, job_id, or role name."
        )
    }


def _ask_what_to_update(state, job):
    """Load job into state and ask the recruiter what to change."""
    current = (
        f"  📌 Role:       {job.get('role')}\n"
        f"  🏢 Company:    {job.get('company_name')}\n"
        f"  📍 Location:   {job.get('location')}\n"
        f"  💼 Experience: {job.get('experience')}\n"
        f"  🛠  Skills:     {', '.join(job.get('skills', []))}"
    )
    return {
        **state,
        "job_id":   job.get("job_id"),
        "job_data": job,
        "stage":    "update_pending",
        "response": (
            f"Here's the current job details:\n\n{current}\n\n"
            "What would you like to update?"
        )
    }
