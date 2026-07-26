REQUIRED_FIELDS=[
    "skills",
    "total_experience_years",
    "preferred_work_type",
    "preferred_locations",
    "expected_salary_min",
    "expected_salary_max",
    "currency",
    "notice_period_days",
    "career_goals"
]

def detect_missing_fields(state):
    print("detect missing")
    profile_data=state.get("profile_data",{}) or {}
    missing=[]
    for field in REQUIRED_FIELDS:
        value=profile_data.get(field)
        if value is None or value=="" or value==[]:
            missing.append(field)
    
    is_complete=len(missing)==0
    print("missing:",missing)
    

    return{
        **state,
        "missing_fields": missing,
        "is_complete": is_complete
    }