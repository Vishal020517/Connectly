def ask_update_node(state):
    """
    Runs after load_profile_node, so profile_data is already populated.
    Shows the current profile values and asks the user what to change.
    Sets stage = 'update_pending' so the next user message goes straight
    into extraction instead of re-running intent detection.
    """
    profile_data = state.get("profile_data", {})

    current = (
        f"  🛠  Skills:       {profile_data.get('skills')}\n"
        f"  📊 Experience:   {profile_data.get('total_experience_years')} yrs\n"
        f"  💰 Salary:       {profile_data.get('expected_salary_min')} - "
        f"{profile_data.get('expected_salary_max')} {profile_data.get('currency')}\n"
        f"  📍 Location:     {profile_data.get('preferred_locations')}\n"
        f"  🏢 Work type:    {profile_data.get('preferred_work_type')}\n"
        f"  ⏳ Notice:       {profile_data.get('notice_period_days')} days\n"
        f"  🎯 Goals:        {profile_data.get('career_goals')}"
    )

    return {
        **state,
        "stage": "update_pending",
        "response": (
            f"Here's your current profile:\n\n{current}\n\n"
            "What would you like to update?"
        )
    }