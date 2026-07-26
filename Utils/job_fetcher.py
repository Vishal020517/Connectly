from Recruiter_module.DB.job_store import collection

def fetch_jobs_by_ids(job_ids):
    jobs = list(collection.find(
        {"job_id": {"$in": job_ids}},
        {"_id": 0}
    ))

    return jobs