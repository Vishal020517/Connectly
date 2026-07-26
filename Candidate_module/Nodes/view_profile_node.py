from Candidate_module.DB.mongo import collection


def view_profile(state):
    user_id    = state.get("user_id")
    profile_id = state.get("profile_id")

    if not user_id:
        return {
            **state,
            "error": "No user_id found. Cannot fetch profile."
        }

    # --- If a specific profile is already selected, show it ---
    if profile_id:
        profile = collection.find_one(
            {"user_id": user_id, "profile_id": profile_id},
            {"_id": 0}
        )

        if not profile:
            return {
                **state,
                "error": f"Profile '{profile_id}' not found for your account."
            }

        return {
            **state,
            "response": _format_profile(profile)
        }

    # --- No profile selected: check how many this user has ---
    profiles = list(collection.find({"user_id": user_id}, {"_id": 0}))

    if not profiles:
        return {
            **state,
            "error": "No profiles found. Create one by telling me about yourself."
        }

    if len(profiles) == 1:
        # Only one profile — show it directly
        return {
            **state,
            "response": _format_profile(profiles[0])
        }

    # Multiple profiles — list them so the user can pick
    profile_list = "\n".join(
        f"{i+1}. Profile ID: {p.get('profile_id')}  |  "
        f"Skills: {', '.join(p.get('skills', []))}"
        for i, p in enumerate(profiles)
    )

    return {
        **state,
        "available_profiles": profiles,
        "response": (
            f"You have {len(profiles)} profiles:\n\n"
            f"{profile_list}\n\n"
            "Reply with a Profile ID to view the full details."
        )
    }


def _format_profile(profile: dict) -> str:
    """Render a profile document as a readable string."""
    return (
        f"\n👤 Your Profile (ID: {profile.get('profile_id')}):\n\n"
        f"🛠  Skills:            {profile.get('skills')}\n"
        f"📊 Experience:        {profile.get('total_experience_years')} years\n"
        f"💰 Salary Expectation:{profile.get('expected_salary_min')} - "
        f"{profile.get('expected_salary_max')} {profile.get('currency')}\n"
        f"📍 Preferred Location:{profile.get('preferred_locations')}\n"
        f"🏢 Work Type:         {profile.get('preferred_work_type')}\n"
        f"⏳ Notice Period:     {profile.get('notice_period_days')} days\n"
        f"🎯 Career Goals:      {profile.get('career_goals')}\n"
        f"✅ Completeness:      {round(profile.get('profile_completeness', 0) * 100)}%\n"
    )
