def job_to_text(job_data: dict) -> str:
    return f"""
    Role: {job_data.get("role")}
    Skills: {", ".join(job_data.get("skills", []))}
    Experience: {job_data.get("experience")}
    Location: {job_data.get("location")}
    Company: {job_data.get("company_name")}
    """