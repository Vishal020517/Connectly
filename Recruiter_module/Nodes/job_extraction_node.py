from Recruiter_module.Chains.job_extraction_chain import extract_job_entities

def job_extraction_node(state):
   
    user_query = state["user_query"]

    extracted_job = extract_job_entities(user_query)
    extracted_dict = extracted_job.model_dump()

    print("extracted job:", extracted_dict)
    
    return {
        **state,
        "extracted_job": extracted_dict
    }