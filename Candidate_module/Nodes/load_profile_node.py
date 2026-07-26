from Candidate_module.DB.mongo import collection


def load_profile(state):
    user_id    = state.get("user_id")
    profile_id = state.get("profile_id")

    if not user_id:
        return {
            **state,
            "error": "No user_id found. Cannot load profile."
        }

    # --- If a specific profile_id is already selected, load it directly ---
    if profile_id:
        profile = collection.find_one(
            {"user_id": user_id, "profile_id": profile_id}
        )

        if not profile:
            return {
                **state,
                "error": f"Profile '{profile_id}' not found for your account."
            }

        profile_data = {
            k: v for k, v in profile.items()
            if k not in ["_id", "user_id", "profile_id", "created_at", "updated_at"]
        }

        print("Loaded profile:", profile_data)

        return {
            **state,
            "profile_data": profile_data,
            "profile_id":   profile_id
        }

    # --- No profile_id selected: fetch all profiles for this user ---
    # We return the list in `available_profiles` so the graph can prompt
    # the candidate to pick one. The calling node / frontend should then
    # set `profile_id` in state and reinvoke.
    profiles = list(collection.find({"user_id": user_id}, {"_id": 0}))

    if not profiles:
        return {
            **state,
            "error": "No profiles found. Please create a profile first."
        }

    if len(profiles) == 1:
        # Only one profile — load it automatically, no need to ask
        profile      = profiles[0]
        profile_data = {
            k: v for k, v in profile.items()
            if k not in ["_id", "user_id", "profile_id", "created_at", "updated_at"]
        }
        print("Auto-loaded single profile:", profile_data)
        return {
            **state,
            "profile_data":       profile_data,
            "profile_id":         profile["profile_id"],
            "available_profiles": profiles
        }

    # Multiple profiles — surface the list so the user can choose
    profile_list = "\n".join(
        f"{i+1}. Profile ID: {p.get('profile_id')}  |  "
        f"Skills: {', '.join(p.get('skills', []))}"
        for i, p in enumerate(profiles)
    )

    return {
        **state,
        "available_profiles": profiles,
        "response": (
            f"You have {len(profiles)} profiles. Which one do you want to update?\n\n"
            f"{profile_list}\n\n"
            "Reply with the Profile ID or the number."
        )
    }
