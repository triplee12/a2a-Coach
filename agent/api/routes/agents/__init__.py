from fastapi import APIRouter
from agent.api.routes.agents.a2a import router as agents_router

router = APIRouter()

router.include_router(agents_router, prefix="/agents", tags=["Agents"])
