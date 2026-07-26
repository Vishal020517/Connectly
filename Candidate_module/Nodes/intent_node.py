import re
from Candidate_module.Chains.Intent_chain import classify_intent
from Candidate_module.Schema.IntentAgentState import CandidateState

# Matches a bare UUID anywhere in the user's message
_UUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)


def intent_node(state: CandidateState) -> CandidateState:
    user_query = state["user_query"]

    if state.get("stage") == "followup":
        print("⚠️ Follow-up mode → skipping intent detection")
        return {
            **state,
            "intent": "create_profile"
        }

    # When we asked "what would you like to update?", the user's next
    # message contains the actual changes — skip LLM intent and go straight
    # to extraction with the update intent preserved.
    if state.get("stage") == "update_pending":
        user_query_lower = state.get("user_query", "").lower()
        view_triggers = ["view", "show", "see my profile", "list"]
        if any(t in user_query_lower for t in view_triggers):
            pass  # fall through to normal intent detection
        else:
            print("✏️ Update pending → routing to extraction with user changes")
            return {
                **state,
                "intent":   "update_profile",
                "stage":    "update_pending_extract",
                "response": "",   # clear the "What would you like to update?" message
            }

    # --- If available_profiles is set, the user was asked to pick one.
    # Check their reply for a UUID or a list number before calling the LLM. ---
    if state.get("available_profiles"):
        profiles = state["available_profiles"]

        # Try to match a UUID in the message
        match = _UUID_RE.search(user_query)
        if match:
            chosen_id = match.group(0)
            print(f"📌 User selected profile_id from message: {chosen_id}")
            return {
                **state,
                "profile_id":           chosen_id,
                "available_profiles":   None,
                "confirmation_message": None,
                "response":             "",
                # preserve whatever intent was active (view/update/delete)
                "intent": state.get("intent", "view_profile"),
            }

        # Try to match a number like "1" or "2"
        num_match = re.search(r'\b(\d+)\b', user_query)
        if num_match:
            idx = int(num_match.group(1)) - 1
            if 0 <= idx < len(profiles):
                chosen_id = profiles[idx].get("profile_id")
                print(f"📌 User selected profile #{idx+1} → profile_id: {chosen_id}")
                return {
                    **state,
                    "profile_id":           chosen_id,
                    "available_profiles":   None,
                    "confirmation_message": None,
                    "response":             "",
                    "intent": state.get("intent", "view_profile"),
                }

    result = classify_intent(user_query)
    print("Detected intent:", result.intent)

    new_state = {
        **state,
        "intent":     result.intent,
        "confidence": result.confidence,
        "reason":     result.reason
    }

    if result.intent == "create_profile":
        # A fresh create request — reset profile_id and profile_data so
        # MemorySaver's persisted state from a previous profile doesn't
        # bleed in. Without this, save_profile_node sees the old profile_id
        # and takes the update path instead of creating a new document.
        new_state["stage"]                = "profile_building"
        new_state["profile_id"]           = None
        new_state["profile_data"]         = {}
        new_state["extracted_profile"]    = {}
        new_state["missing_fields"]       = []
        new_state["is_complete"]          = False
        new_state["next_question"]        = None
        new_state["confirmation_message"] = None
        new_state["response"]             = ""
        new_state["available_profiles"]   = None
        print("🔄 Fresh create_profile → cleared profile_id and profile_data")

    elif result.intent == "view_profile":
        new_state["confirmation_message"] = None
        new_state["response"]             = ""
        match = _UUID_RE.search(user_query)
        if match:
            new_state["profile_id"]         = match.group(0)
            new_state["available_profiles"] = None
            print(f"📌 UUID found in view_profile query: {match.group(0)}")

    elif result.intent == "delete_profile":
        new_state["confirmation_message"] = None
        new_state["response"]             = ""
        match = _UUID_RE.search(user_query)
        if match:
            new_state["profile_id"]         = match.group(0)
            new_state["available_profiles"] = None
            print(f"📌 UUID found in delete_profile query: {match.group(0)}")

    elif result.intent == "update_profile":
        new_state["confirmation_message"] = None
        new_state["response"]             = ""
        # Also pick up a UUID if the user specified a profile to update
        match = _UUID_RE.search(user_query)
        if match:
            new_state["profile_id"]         = match.group(0)
            new_state["available_profiles"] = None
            print(f"📌 UUID found in update_profile query: {match.group(0)}")

    return new_state

def route_based_on_intent(state: CandidateState) -> str:
    """
    Determines which node to go next based on intent.
    """

    if state.get("stage") == "followup":
        return "create_profile"

    # update_pending means the user just replied with their actual changes —
    # skip load (profile_data is already in state) and go straight to extract.
    if state.get("stage") == "update_pending_extract":
        return "extract_profile"    
    intent = state["intent"]

    print("Routing intent:", intent)

    if intent == "create_profile":
        return "create_profile"

    elif intent == "update_profile":
        return "update_profile"

    elif intent == "job_search":
        return "job_search"
    
    elif intent == "resume_upload":
        return "resume_upload" 
    
    elif intent == "view_profile":
        return "view_profile"
    
    elif intent == "delete_profile":
        return "delete_profile"

    else:
        return "general_query"

def route_after_missing(state):
    if state["intent"]=="update_profile":
        return "save_profile"
    if state["is_complete"]:
        return "save_profile"
    else:
        return "ask_followup"

def route_after_extraction(state):
    if state["intent"] == "update_profile":
        return "merge"

    return "detect"

if __name__=="__main__":
    test_queries = [
        "I need to add my skills"
    ]

    for query in test_queries:
        result = classify_intent(query)

        print("\n---------------------------")
        print("Query:", query)
        print("Intent:", result.intent)
        print("Confidence:", result.confidence)
        print("Reason:", result.reason)