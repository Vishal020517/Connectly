from fastapi import APIRouter, HTTPException
from backend.models import ChatRequest, ChatResponse
from backend.state_store import get_candidate_state, set_candidate_state

# Import the compiled graph
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from Candidate_module.Graph.intent_graph import intent_graph

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def candidate_chat(req: ChatRequest):
    """
    Single endpoint for all candidate chat turns.
    The frontend sends user_id + message every turn.
    We load the current state, invoke the graph, save the updated state,
    and return the AI reply + any updated IDs.
    """
    thread_id = req.session_id or req.user_id
    state = get_candidate_state(req.user_id, thread_id)

    # Apply any IDs the frontend is tracking
    state["user_query"] = req.message
    if req.profile_id:
        state["profile_id"] = req.profile_id

    config = {"configurable": {"thread_id": thread_id}}

    try:
        updated = intent_graph.invoke(state, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    set_candidate_state(req.user_id, updated, thread_id)

    # Pick the right reply field (priority order)
    reply = (
        updated.get("next_question")
        or updated.get("response")
        or updated.get("confirmation_message")
        or updated.get("error")
        or "Done"
    )

    return ChatResponse(
        reply=reply,
        user_id=req.user_id,
        profile_id=updated.get("profile_id"),
        intent=updated.get("intent"),
        stage=updated.get("stage"),
        available_profiles=updated.get("available_profiles"),
    )
