from fastapi import APIRouter, HTTPException
from backend.models import ChatRequest, ChatResponse
from backend.state_store import get_recruiter_state, set_recruiter_state

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from Recruiter_module.Graph.recruiter_graph import recruiter_graph

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def recruiter_chat(req: ChatRequest):
    """
    Single endpoint for all recruiter chat turns.
    """
    thread_id = req.session_id or req.user_id
    state = get_recruiter_state(req.user_id, thread_id)

    state["user_query"] = req.message
    if req.job_id:
        state["job_id"] = req.job_id

    config = {"configurable": {"thread_id": thread_id}}

    try:
        updated = recruiter_graph.invoke(state, config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    set_recruiter_state(req.user_id, updated, thread_id)

    reply = (
        updated.get("next_question")
        or updated.get("response")
        or updated.get("error")
        or "Done"
    )

    return ChatResponse(
        reply=reply,
        user_id=req.user_id,
        job_id=updated.get("job_id"),
        intent=updated.get("intent"),
        stage=updated.get("stage"),
        available_jobs=updated.get("available_jobs"),
    )
