import re
from Recruiter_module.Chains.intent_chain import classify_recruiter_intent
from Recruiter_module.Schema.recruiter_state import RecruiterState
from Recruiter_module.DB.job_store import collection

_UUID_RE = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    re.IGNORECASE
)


def recruiter_intent_node(state: RecruiterState) -> RecruiterState:
    user_input = state["user_query"]

    # --- Follow-up: collecting missing job fields ---
    if state.get("stage") == "followup":
        print("⚠️ Follow-up mode → skipping intent detection")
        return {**state, "intent": "Create_job"}

    # --- delete_pending: user was asked which job to delete ---
    if state.get("stage") == "delete_pending":
        resolved = _resolve_job_selection(state, user_input)
        if resolved:
            print(f"🗑️ Delete pending → job_id resolved: {resolved}")
            return {
                **state,
                "job_id":         resolved,
                "available_jobs": None,
                "stage":          "delete_confirmed",
                "response":       "",
                "intent":         "Delete_job",
            }
        # Couldn't resolve — let it fall through to normal intent detection

    # --- update_pending: user was asked what to change ---
    if state.get("stage") == "update_pending":
        view_triggers = ["view", "show", "list", "see my jobs"]
        if not any(t in user_input.lower() for t in view_triggers):
            print("✏️ Update pending → routing to extraction with changes")
            return {
                **state,
                "intent": "Update_job",
                "stage":  "update_pending_extract",
                "response": "",
            }

    # --- update_job_select: user was asked which job to update ---
    if state.get("stage") == "update_job_select":
        resolved = _resolve_job_selection(state, user_input)
        if resolved:
            print(f"✏️ Update job_select → job_id resolved: {resolved}")
            return {
                **state,
                "job_id":         resolved,
                "available_jobs": None,
                "stage":          "update_pending",
                "response":       "",
                "intent":         "Update_job",
            }

    intent_result = classify_recruiter_intent(user_input)
    print("Detected intent:", intent_result.intent)

    new_state = {
        **state,
        "intent":     intent_result.intent,
        "confidence": intent_result.confidence,
        "reason":     intent_result.reason,
    }

    # Clear stale messages on fresh intents
    if intent_result.intent in ("Delete_job", "Update_job", "View_jobs"):
        new_state["response"] = ""

    # If a UUID appears in the query, capture it immediately
    match = _UUID_RE.search(user_input)
    if match and intent_result.intent in ("Delete_job", "Update_job"):
        new_state["job_id"]         = match.group(0)
        new_state["available_jobs"] = None
        print(f"📌 UUID found in query: {match.group(0)}")

    return new_state


def _resolve_job_selection(state, user_input):
    """
    Try to resolve a job_id from the user's reply.
    Checks for UUID directly, then a list number against available_jobs.
    Falls back to matching role name against the recruiter's jobs in MongoDB.
    """
    # 1. UUID in message
    match = _UUID_RE.search(user_input)
    if match:
        return match.group(0)

    # 2. Number like "1" or "2"
    available = state.get("available_jobs", []) or []
    num_match = re.search(r'\b(\d+)\b', user_input)
    if num_match:
        idx = int(num_match.group(1)) - 1
        if 0 <= idx < len(available):
            return available[idx].get("job_id")

    # 3. Role name match against available_jobs list
    if available:
        lower = user_input.lower()
        for job in available:
            if job.get("role", "").lower() in lower:
                return job.get("job_id")

    return None
