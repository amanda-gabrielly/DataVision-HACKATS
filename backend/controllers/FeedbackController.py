
from fastapi import APIRouter

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/")
async def enviar_feedback(dados: dict):
    # Chamar FeedbackService.
    pass
