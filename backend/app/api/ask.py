from fastapi import APIRouter

from app.models.schemas import AskRequest, AskResponse
from app.services.llm_service import ask_llm


router = APIRouter(prefix="/api", tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    history = [msg.dict() for msg in request.history]

    answer = ask_llm(
        question=request.question,
        subject=request.subject,
        history=history,
    )

    return AskResponse(answer=answer)
