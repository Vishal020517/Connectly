from datetime import datetime
from Recruiter_module.DB.job_store import collection
import uuid
from Utils.job_to_text import job_to_text
from Utils.embedder import generate_embeddings
from Utils.vector_store import store_job_embedding
from Recruiter_module.Chains.job_description_chain import generate_job_description



def save_job_node(state):
    job_data=state.get("job_data")

    if not job_data:
        return{
            **state,
            "error":"No job data to save"
        }
    
    if not job_data.get("job_description"):
        print("Generating Job Description...")
        job_data["job_description"]=generate_job_description(job_data)
    
    try:
        job_id=str(uuid.uuid4())
        document={
            "job_id":job_id,
            # recruiter_id ties this job to the recruiter who created it.
            # Every query (view/update/delete) will filter by this field
            # so recruiters only ever see and touch their own jobs.
            "recruiter_id": state.get("user_id"),
            **job_data,
            "created_at":datetime.utcnow(),
            "updated_at":datetime.utcnow()
        }
        collection.insert_one(document)
        print("Saved job:",document)

        text=job_to_text(job_data)
        embeddings=generate_embeddings(text)
        store_job_embedding(job_id,embeddings,text)
        print("Job embeddings stored in vector DB")

        return{
            **state,
            "job_id": job_id,
            "job_data":job_data,           
            "missing_fields": [],
            "is_complete":True,
            "stage":None,
            "next_question":None,
            "response": "Job created and saved successfully!"
        }
    
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "response": "Failed to save job."
        }