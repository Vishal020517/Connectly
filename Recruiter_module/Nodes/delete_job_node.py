from Recruiter_module.DB.job_store import collection
from Recruiter_module.Chains.job_extraction_chain import extract_job_entities
import chromadb
from Utils.vector_store import CHROMA_PATH

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
job_chroma        = chroma_client.get_or_create_collection(name="job_embeddings")


def delete_job_node(state):
    recruiter_id = state.get("user_id")
    job_id       = state.get("job_id")
    stage        = state.get("stage")

    if not recruiter_id:
        return {**state, "response": "Could not identify your account."}

    # --- If job_id is confirmed (from selection or UUID in query), delete it ---
    if job_id and stage == "delete_confirmed":
        existing = collection.find_one(
            {"job_id": job_id, "recruiter_id": recruiter_id}
        )
        if not existing:
            return {
                **state,
                "stage":    None,
                "response": "No matching job found in your postings."
            }

        collection.delete_one({"_id": existing["_id"]})
        try:
            job_chroma.delete(ids=[job_id])
        except Exception:
            pass

        return {
            **state,
            "job_id":    None,
            "job_data":  {},
            "stage":     None,
            "response":  f"🗑️ '{existing.get('role')}' at {existing.get('company_name')} deleted successfully."
        }

    # --- job_id already in state from a previous view/create (no need to ask) ---
    if job_id and stage != "delete_pending":
        existing = collection.find_one(
            {"job_id": job_id, "recruiter_id": recruiter_id}
        )
        if existing:
            collection.delete_one({"_id": existing["_id"]})
            try:
                job_chroma.delete(ids=[job_id])
            except Exception:
                pass
            return {
                **state,
                "job_id":    None,
                "job_data":  {},
                "stage":     None,
                "response":  f"🗑️ '{existing.get('role')}' at {existing.get('company_name')} deleted successfully."
            }

    # --- No job_id: try to extract role from query ---
    user_query = state.get("user_query", "")
    extracted  = extract_job_entities(user_query)
    role       = extracted.model_dump().get("role", "")

    if role:
        existing = collection.find_one(
            {"role": role, "recruiter_id": recruiter_id}
        )
        if existing:
            collection.delete_one({"_id": existing["_id"]})
            try:
                job_chroma.delete(ids=[existing["job_id"]])
            except Exception:
                pass
            return {
                **state,
                "job_id":    None,
                "job_data":  {},
                "stage":     None,
                "response":  f"🗑️ '{existing.get('role')}' at {existing.get('company_name')} deleted successfully."
            }

    # --- Vague request — show the recruiter's jobs and ask them to pick ---
    jobs = list(collection.find(
        {"recruiter_id": recruiter_id}, {"_id": 0}
    ))

    if not jobs:
        return {**state, "response": "You have no job postings to delete."}

    if len(jobs) == 1:
        # Only one job — confirm and delete directly
        j = jobs[0]
        collection.delete_one({"job_id": j["job_id"], "recruiter_id": recruiter_id})
        try:
            job_chroma.delete(ids=[j["job_id"]])
        except Exception:
            pass
        return {
            **state,
            "job_id":    None,
            "job_data":  {},
            "stage":     None,
            "response":  f"🗑️ '{j.get('role')}' at {j.get('company_name')} deleted successfully."
        }

    # Multiple jobs — ask which one
    job_list = "\n".join(
        f"{i+1}. {j.get('role')} at {j.get('company_name')}  |  job_id: {j.get('job_id')}"
        for i, j in enumerate(jobs)
    )

    return {
        **state,
        "available_jobs": jobs,
        "stage":          "delete_pending",
        "response": (
            f"Which job would you like to delete?\n\n{job_list}\n\n"
            "Reply with the job number, job_id, or role name."
        )
    }
