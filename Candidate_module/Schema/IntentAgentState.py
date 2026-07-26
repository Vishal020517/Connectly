from typing import TypedDict, Optional, List, Dict, Any, Annotated


class CandidateState(TypedDict):
    user_query: str

    # user_id identifies the candidate across sessions.
    # Generated on first profile save and reused for all subsequent turns.
    user_id: Optional[str]

    # profile_id identifies the specific profile being worked on.
    # A single candidate (user_id) can have multiple profiles.
    # Set automatically when there's only one profile, or after the user
    # picks one from the available_profiles list.
    profile_id: Optional[str]

    intent: str
    confidence: float
    reason: str

    # profile_data holds the in-progress or loaded profile for this turn.
    profile_data: Annotated[dict, "persist"]
    extracted_profile: dict

    # available_profiles is populated by load/view nodes when the user has
    # more than one profile, so the conversation can ask them to pick one.
    available_profiles: Optional[List[Dict[str, Any]]]

    missing_fields: List[str]
    next_question: Optional[str]

    is_complete: Optional[bool]
    stage: Optional[str]
    error: Optional[str]

    # confirmation_message is set by save_profile_node after a successful save/update.
    confirmation_message: Optional[str]

    response: str
