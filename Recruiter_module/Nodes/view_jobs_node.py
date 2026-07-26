from Recruiter_module.DB.job_store import collection

def view_jobs(state):
    recruiter_id = state.get("user_id")

    if not recruiter_id:
        return {
            **state,
            "response": "Could not identify your account. Please provide your recruiter ID."
        }

    # Filter strictly by recruiter_id so a recruiter only sees
    # the jobs they personally posted — never another recruiter's listings.
    jobs = list(collection.find({"recruiter_id": recruiter_id}, {"_id": 0}))

    if not jobs:
        return {
            **state,
            "response": "You have no job postings yet. Create one by describing the role."
        }

    response = "📋 Your job postings:\n\n"

    for i, job in enumerate(jobs, 1):
        response += (
            f"{i}. {job.get('role')} at {job.get('company_name')} "
            f"({job.get('location')})  |  job_id: {job.get('job_id')}\n"
        )

    # Store the list in state so other nodes (update/delete) can
    # reference jobs by index or job_id without re-querying.
    return {
        **state,
        "available_jobs": jobs,
        "response": response
    }
