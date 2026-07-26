def merge_update(state):
    existing=state.get("profile_data",{})
    new_data=state.get("extracted_profile",{})

    updated_profile=existing.copy()

    for key,value in new_data.items():
        if value is not None:
            updated_profile[key]=value
    
    print("Updated profile:",updated_profile)

    return{
        **state,
        "profile_data":updated_profile
    }