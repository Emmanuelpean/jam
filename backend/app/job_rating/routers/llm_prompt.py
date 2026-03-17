"""Routers for Job Rating related endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_rating import schemas


llm_system_prompt_router = APIRouter(prefix="/ai-system-prompts", tags=["ai-system-prompts"])


@llm_system_prompt_router.get("/", response_model=list[schemas.AiSystemPromptOut])
def get_all_ai_system_prompts(
    _current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all AI system prompts."""

    return db.query(models.AiSystemPrompt).all()
