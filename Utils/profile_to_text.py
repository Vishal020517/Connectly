def profile_to_text(profile):
    return f"""
    Skills: {profile.get("skills")}
    Experience: {profile.get("total_experience_years")} years
    Location: {profile.get("preferred_locations")}
    Work Type: {profile.get("preferred_work_type")}
    Salary: {profile.get("expected_salary_min")} to {profile.get("expected_salary_max")} {profile.get("currency")}
    Career Goals: {profile.get("career_goals")}
    """
