REQUIRED_SKILLS=[
    "role",
    "skills",
    "experience",
    "location",
    "company_name",
    "apply_link"
]

def detect_missing_node(state):
    print("detect missing")
    job_data=state.get("job_data",{}) or {}
    missing=[]

    for field in REQUIRED_SKILLS:
        value=job_data.get(field)

        if value is None or value == "" or value == []:
            missing.append(field)
        
    is_complete = len(missing) == 0

    print("Missing :",missing)

    return {
        **state,
        "missing_fields": missing,
        "is_complete": is_complete
    }