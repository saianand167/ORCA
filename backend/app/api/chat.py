import uuid
from fastapi import APIRouter
from ..core.models import ChatRequest, ChatResponse
from ..graph.orca_graph import ORCAGraphOrchestrator

router = APIRouter(prefix="/chat", tags=["Conversational Agent"])

@router.post("", response_model=ChatResponse)
async def chat_with_orca(request: ChatRequest):
    conversation_id = request.conversation_id or f"sess_{uuid.uuid4().hex[:8]}"
    return await ORCAGraphOrchestrator.run(
        message=request.message,
        user_type=request.user_type,
        location_id=request.location_id or "visakhapatnam",
        latitude=request.latitude or 17.6868,
        longitude=request.longitude or 83.2185,
        conversation_id=conversation_id,
        demo_mode=request.demo_mode
    )
