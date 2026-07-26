def merge_updated_node(state):
    existing = state.get("job_data", {})
    new_data = state.get("extracted_job", {})

    updated_job = existing.copy()

    for key, value in new_data.items():
        if key == "missing_fields":
            continue

        if value is not None and value != "" and value != []:
            updated_job[key] = value

    print("Updated job:", updated_job)

    return {
        **state,
        "job_data": updated_job
    }