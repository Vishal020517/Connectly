from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from Recruiter_module.Schema.recruiter_state import RecruiterState
from Recruiter_module.Nodes.job_extraction_node import job_extraction_node
from Recruiter_module.Nodes.merge_updated_node import merge_updated_node
from Recruiter_module.Nodes.recruiter_intent_node import recruiter_intent_node
from Recruiter_module.Nodes.detect_missing_node import detect_missing_node
from Recruiter_module.Nodes.followup_node import follow_up_node
from Recruiter_module.Nodes.save_job_node import save_job_node
from Recruiter_module.Nodes.view_jobs_node import view_jobs
from Recruiter_module.Nodes.update_job_node import update_job_node
from Recruiter_module.Nodes.delete_job_node import delete_job_node
from Recruiter_module.Nodes.candidate_matching_node import candidate_matching_node

def route_after_missing_detection(state):
    if state.get("is_complete"):
        if state.get("intent") == "Update_job":
            return "update_job_node"
        return "save_job_node"
    else:
        return "follow_up_node"
    

def route_based_on_intent(state):
    intent = state.get("intent")
    stage  = state.get("stage")

    # update_pending_extract: user replied with changes, skip to update directly
    if stage == "update_pending_extract":
        return "update_job_node"

    # delete_confirmed: user selected a job to delete
    if stage == "delete_confirmed":
        return "delete_job_node"

    if intent == "Create_job":
        return "job_extraction_node"
    elif intent == "Update_job":
        return "update_job_node"
    elif intent == "View_jobs":
        return "view_jobs_node"
    elif intent == "Delete_job":
        return "delete_job_node"
    elif intent == "Search_candidates":
        return "candidate_matching_node"
    else:
        return "general_node"

def general_node(state):
    return {
        **state,
        "response": "I can help you create, view, update, or delete jobs."
    }

builder=StateGraph(RecruiterState)

builder.add_node("intent_detection_node",recruiter_intent_node)
builder.add_node("job_extraction_node",job_extraction_node)
builder.add_node("merge_update_node",merge_updated_node)
builder.add_node("detect_missing_node",detect_missing_node)
builder.add_node("follow_up_node",follow_up_node)
builder.add_node("save_job_node",save_job_node)
builder.add_node("view_jobs_node",view_jobs)
builder.add_node("update_job_node",update_job_node)
builder.add_node("delete_job_node",delete_job_node)
builder.add_node("general_node",general_node)
builder.add_node("candidate_matching_node",candidate_matching_node)

builder.set_entry_point("intent_detection_node")

builder.add_conditional_edges(
    "intent_detection_node",
    route_based_on_intent,
    {
        "job_extraction_node": "job_extraction_node",
        "view_jobs_node": "view_jobs_node",
        "delete_job_node": "delete_job_node",
        "general_node":"general_node",
        "update_job_node":"update_job_node",
        "candidate_matching_node":"candidate_matching_node"
    }
)
builder.add_edge("job_extraction_node","merge_update_node")
builder.add_edge("merge_update_node","detect_missing_node")    

builder.add_conditional_edges(
    "detect_missing_node",
    route_after_missing_detection,
    {
        "follow_up_node":  "follow_up_node",
        "save_job_node":   "save_job_node",
        "update_job_node": "update_job_node",
    }
)

builder.add_edge("follow_up_node",END)
builder.add_edge("save_job_node",END)
builder.add_edge("view_jobs_node",END)
builder.add_edge("delete_job_node", END)
builder.add_edge("update_job_node",END)
builder.add_edge("general_node",END)
builder.add_edge("candidate_matching_node", END)

# MemorySaver persists the entire RecruiterState between turns keyed by
# thread_id. Pass config={"configurable": {"thread_id": user_id}} when
# invoking the graph so each recruiter's session is isolated.
memory = MemorySaver()
recruiter_graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    # Unique recruiter identifier. In production comes from your auth layer.
    user_id = "recruiter_1"

    state = {
        "user_query": "",
        "user_id": user_id,
        "job_id": None,

        "intent": "",
        "confidence": 0.0,
        "reason": "",

        "job_data": {},
        "extracted_job": {},
        "available_jobs": None,

        "missing_fields": [],
        "next_question": None,

        "is_complete": False,
        "stage": None,
        "error": None,

        "response": ""
    }

    print("\n--- Recruiter Chat (with session persistence) ---\n")
    print(f"Session ID: {user_id}\n")

    while True:
        user_input = input("Recruiter: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        state["user_query"] = user_input

        # thread_id isolates each recruiter's session — recruiter_1 and
        # recruiter_2 running simultaneously won't share any state.
        config = {"configurable": {"thread_id": user_id}}
        state = recruiter_graph.invoke(state, config)

        if state.get("next_question"):
            print("\n🤖:", state["next_question"])
        elif state.get("error"):
            print("\n⚠️ Error:", state["error"])
        else:
            print("\n🤖:", state.get("response", "Done"))

        print("\n📋 Current Job Data:", state.get("job_data"))
        print(f"🆔 Job ID: {state.get('job_id')}")
        print("-" * 50)