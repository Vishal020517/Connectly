from Candidate_module.Chains.Profile_extraction_chain import extract_profile_data

def profile_extraction_node(state):
   
    user_query = state["user_query"]
    extracted_profile = extract_profile_data(user_query)
    extracted_dict = extracted_profile.model_dump()
    print("extracted text:",extracted_dict)
    
    return{
        **state,
        "extracted_profile":extracted_dict
    }
