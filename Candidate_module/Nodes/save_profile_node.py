from datetime import datetime
from Candidate_module.DB.mongo import collection
import uuid
from Utils.profile_to_text import profile_to_text
from Utils.embedder import generate_embeddings
from Utils.vector_store import store_embedding


REQUIRED_FIELDS = [
    "skills",
    "total_experience_years",
    "expected_salary_min",
    "expected_salary_max",
    "preferred_locations",
    "preferred_work_type",
    "notice_period_days",
    "career_goals",
    "currency"
]


def save_profile_node(state):
    profile_data = state.get("profile_data")

    if not profile_data:
        return {
            **state,
            "error": "No profile data to save."
        }

    # Calculate how complete the profile is (0.0 → 1.0)
    filled = sum(
        1 for f in REQUIRED_FIELDS
        if profile_data.get(f) not in [None, "", []]
    )
    completeness = filled / len(REQUIRED_FIELDS)

    user_id    = state.get("user_id")
    profile_id = state.get("profile_id")   # set when updating an existing profile

    if profile_id:
        # --- UPDATE path ---
        # profile_id is set only when the candidate explicitly loaded a specific
        # profile to edit. We target that exact document so we never overwrite
        # a different profile belonging to the same user.
        collection.update_one(
            {"profile_id": profile_id, "user_id": user_id},
            {
                "$set": {
                    **profile_data,
                    "profile_completeness": completeness,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        message = "✅ Profile updated successfully."

    else:
        # --- CREATE path ---
        # Each new profile gets its own profile_id (UUID).
        # user_id links it back to the candidate's account so they can
        # have multiple profiles (e.g. one for ML roles, one for backend).
        if not user_id:
            user_id = str(uuid.uuid4())

        profile_id = str(uuid.uuid4())

        document = {
            "user_id":    user_id,
            "profile_id": profile_id,
            **profile_data,
            "profile_completeness": completeness,
            "extracted_from": "conversation",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        collection.insert_one(document)
        message = "✅ Profile created successfully."

    # Store embedding so this profile is searchable by recruiters
    text       = profile_to_text(profile_data)
    embeddings = generate_embeddings(text)
    # Use profile_id as the vector store key so each profile has
    # its own independent embedding (not overwritten on the second profile).
    store_embedding(profile_id, embeddings, text)

    print("Embeddings stored in ChromaDB for profile_id:", profile_id)

    return {
        **state,
        "user_id":              user_id,
        "profile_id":           profile_id,
        "confirmation_message": message,
        "response":             "",        # clear stale ask_update response
        "stage":                None,      # exit update_pending loop
        "next_question":        None,
        "missing_fields":       [],
        "is_complete":          True,
    }
