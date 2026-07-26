from Candidate_module.DB.mongo import collection


def fetch_candidates_by_ids(profile_ids):
    """
    Fetch candidate profiles from MongoDB by profile_id.

    ChromaDB now stores embeddings keyed by profile_id (not user_id) so that
    each profile has its own independent embedding. This function mirrors that
    by querying MongoDB on profile_id as well.
    """
    candidates = list(collection.find(
        {"profile_id": {"$in": profile_ids}},
        {"_id": 0}
    ))
    return candidates
