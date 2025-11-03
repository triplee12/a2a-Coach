from fastapi import APIRouter
from agent.core.config import PROJECT_NAME

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/status")
async def health_check() -> dict:
    status = {"status": "ok", "agent": PROJECT_NAME}
    return status