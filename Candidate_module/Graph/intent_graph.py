from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from Candidate_module.Chains.Intent_chain import classify_intent
from Candidate_module.Nodes.follow_up_node import follow_up_node
from Candidate_module.Nodes.profile_extraction_node import profile_extraction_node
from Candidate_module.Schema.IntentAgentState import CandidateState
from Candidate_module.Nodes.intent_node import intent_node, route_after_missing, route_based_on_intent, route_after_extraction
from Candidate_module.Nodes.detect_missing_nodes import detect_missing_fields
from Candidate_module.Nodes.save_profile_node import save_profile_node
from Candidate_module.Nodes.load_profile_node import load_profile
from Candidate_module.Nodes.merge_updated_node import merge_update
from Candidate_module.Nodes.view_profile_node import view_profile
from Candidate_module.Nodes.job_matching_node import job_matching_node
from Candidate_module.Nodes.ask_update_node import ask_update_node
from Candidate_module.Nodes.delete_profile_node import delete_profile_node

workflow = StateGraph(CandidateState)
workflow.add_node("intent_node", intent_node)
workflow.set_entry_point("intent_node")
workflow.add_node("extract_profile_node", profile_extraction_node)
workflow.add_node("detect_missing_fields", detect_missing_fields)
workflow.add_node("ask_followup_node", follow_up_node)
workflow.add_node("save_profile_node", save_profile_node)
workflow.add_node("load_profile_node", load_profile)
workflow.add_node("merge_updated_node", merge_update)
workflow.add_node("view_profile_node", view_profile)
workflow.add_node("job_matching_node", job_matching_node)
workflow.add_node("ask_update_node", ask_update_node)
workflow.add_node("delete_profile_node", delete_profile_node)

workflow.add_conditional_edges(
    "intent_node",
    route_based_on_intent,
    {
        "create_profile":    "extract_profile_node",
        "update_profile":    "load_profile_node",
        "extract_profile":   "extract_profile_node",   # update_pending_extract bypasses load
        "view_profile":      "view_profile_node",
        "delete_profile":    "delete_profile_node",
        "job_search":        "job_matching_node",
        "general_query":     END,
    }
)

# After loading the profile, decide whether the user already told us
# what to change (go straight to extraction) or just said "edit my profile"
# with no details (ask them what to change first).
def route_after_load(state):
    # If available_profiles was returned, the user needs to pick one first —
    # go to END and wait. intent_node will handle the UUID reply next turn.
    if state.get("available_profiles") and not state.get("profile_id"):
        return "end"

    user_query = state.get("user_query", "").lower()
    # Vague if the message has no field-specific update info
    vague_triggers = ["edit", "update", "change", "modify", "i need to edit",
                      "i want to edit", "i want to update", "i need to update"]
    is_vague = any(t in user_query for t in vague_triggers) and len(user_query.split()) < 10

    # Also vague if the user just sent a UUID (they just selected a profile)
    import re
    uuid_only = bool(re.fullmatch(
        r'\s*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\s*',
        user_query, re.IGNORECASE
    ))

    if is_vague or uuid_only:
        return "ask_update"
    return "extract"

workflow.add_conditional_edges(
    "load_profile_node",
    route_after_load,
    {
        "ask_update": "ask_update_node",
        "extract":    "extract_profile_node",
        "end":        END,
    }
)

workflow.add_edge("ask_update_node", END)   # pause and wait for user's reply
workflow.add_edge("extract_profile_node", "merge_updated_node")
workflow.add_edge("merge_updated_node", "detect_missing_fields")

workflow.add_conditional_edges(
    "detect_missing_fields",
    route_after_missing,
    {
        "save_profile":  "save_profile_node",
        "ask_followup":  "ask_followup_node"
    }
)

workflow.add_edge("save_profile_node", END)
workflow.add_edge("view_profile_node", END)
workflow.add_edge("delete_profile_node", END)
workflow.add_edge("job_matching_node", END)

# MemorySaver persists the entire CandidateState between turns keyed by
# thread_id. Pass config={"configurable": {"thread_id": user_id}} when
# invoking the graph and the session is automatically resumed.
memory = MemorySaver()
intent_graph = workflow.compile(
    checkpointer=memory,
    interrupt_after=["ask_followup_node"]
)



# if __name__ == "__main__":

#     png_bytes = intent_graph.get_graph().draw_mermaid_png()

#     with open("intent_graph.png", "wb") as f:
#         f.write(png_bytes)
#     # -----------------------------
#     # Initial Test State
#     # -----------------------------
#     state = {
#         "user_query":"I am experienced in C# for 2 years i would like to work in remote jobs in trichy with salary of 7 to 8lpa and my goal is become an ceo can you create me an profile",
#         "user_id":None,
#         "intent": None,
#         "confidence": None,
#         "reasoning": None,
#         "profile_data": {},
#         "missing_fields": [],
#         "next_question": None,
#         "is_complete": None,
#         "stage": None,
#         "error": None,
#         "saved_profile_id": None,
#         "confirmation_message": None
#     }

#     while True:
#         print("Running Graph...")

#         state = intent_graph.invoke(state)

#         print("\nCurrent State:")
#         print("Profile Data:", state.get("profile_data"))
#         print("Missing Fields:", state.get("missing_fields"))
#         print("Next Question:", state.get("next_question"))
#         print("Is Complete:", state.get("is_complete"))

#         if state.get("is_complete"):
#             print("\nProfile creation complete!")
#             break

#         user_input = input("\nYour response: ")

#         state = {
#             **state,
#             "user_query": user_input
#         }
    
if __name__ == "__main__":
    # Unique user identifier. In production this would come from your auth layer.
    # All conversations for the same user will resume from the last saved state.
    user_id = "test_user_123"

    state = {
        "user_query": "",
        "user_id": user_id,
        "profile_id": None,

        "intent": "",
        "confidence": 0.0,
        "reason": "",

        "profile_data": {},
        "extracted_profile": {},
        "available_profiles": None,

        "missing_fields": [],
        "next_question": None,

        "is_complete": False,
        "stage": None,
        "error": None,
        "confirmation_message": None,

        "response": ""
    }

    print("\n--- Candidate Chat (with session persistence) ---\n")
    print(f"Session ID: {user_id}\n")

    while True:
        user_input = input("Candidate: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        state["user_query"] = user_input

        # thread_id ties this invocation to a persistent session.
        # All state updates are saved after each graph run and restored on the next.
        config = {"configurable": {"thread_id": user_id}}
        state = intent_graph.invoke(state, config)

        # Response handling — response takes priority over confirmation_message
        # so that view/job-search results are never shadowed by a stale save message.
        if state.get("next_question"):
            print("\n🤖:", state["next_question"])
        elif state.get("response"):
            print("\n🤖:", state["response"])
        elif state.get("confirmation_message"):
            print("\n🤖:", state["confirmation_message"])
        elif state.get("error"):
            print("\n⚠️ Error:", state["error"])
        else:
            print("\n🤖: Done")

        # Debug info (optional)
        print("\n📊 Profile Data:", state.get("profile_data"))
        print("⚠️  Missing Fields:", state.get("missing_fields"))
        print(f"🆔 Profile ID: {state.get('profile_id')}")
        print("-" * 50)
