from Candidate_module.DB.mongo import collection
import chromadb
from Utils.vector_store import CHROMA_PATH

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(name="candidates")


def delete_profile_node(state):
    user_id    = state.get("user_id")
    profile_id = state.get("profile_id")

    if not user_id:
        return {
            **state,
            "response": "Could not identify your account. Cannot delete profile."
        }

    # --- If a specific profile_id is already in state, delete just that one ---
    if profile_id:
        result = collection.delete_one({"profile_id": profile_id, "user_id": user_id})

        if result.deleted_count == 0:
            return {
                **state,
                "response": f"No profile found with ID '{profile_id}'."
            }

        # Remove embedding from ChromaDB too
        try:
            chroma_collection.delete(ids=[profile_id])
        except Exception:
            pass  # not fatal if embedding wasn't there

        return {
            **state,
            "profile_id":           None,   # clear from state
            "profile_data":         {},
            "available_profiles":   None,
            "stage":                None,
            "response":             "",
            "confirmation_message": f"🗑️ Profile deleted successfully."
        }

    # --- No profile_id: check how many this user has ---
    profiles = list(collection.find({"user_id": user_id}, {"_id": 0}))

    if not profiles:
        return {
            **state,
            "response": "No profiles found to delete."
        }

    if len(profiles) == 1:
        # Only one — delete it directly
        pid = profiles[0]["profile_id"]
        collection.delete_one({"profile_id": pid, "user_id": user_id})
        try:
            chroma_collection.delete(ids=[pid])
        except Exception:
            pass

        return {
            **state,
            "profile_id":           None,
            "profile_data":         {},
            "available_profiles":   None,
            "stage":                None,
            "response":             "",
            "confirmation_message": "🗑️ Profile deleted successfully."
        }

    # Multiple profiles — ask the user which one to delete
    profile_list = "\n".join(
        f"{i+1}. Profile ID: {p.get('profile_id')}  |  "
        f"Skills: {', '.join(p.get('skills', []))}"
        for i, p in enumerate(profiles)
    )

    return {
        **state,
        "available_profiles": profiles,
        "response": (
            f"You have {len(profiles)} profiles. Which one do you want to delete?\n\n"
            f"{profile_list}\n\n"
            "Reply with the Profile ID or the number."
        )
    }
