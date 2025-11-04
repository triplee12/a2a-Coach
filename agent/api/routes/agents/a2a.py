import json
import uuid
from typing import Optional
import redis
from fastapi import APIRouter, Depends, Request, Header, HTTPException
from agent.models.agent_rpc import JsonRpcRequest, JsonRpcResponse, TelexRequest, TelexResponse
from agent.core.config import PROJECT_NAME, AGENT_API_KEY, TELEX_LOG_BASE
from agent.core.logger import logger
from agent.db.database import get_redis, get_repository
from agent.services.agent import run_gemini
# from agent.db.repositories.goals import GoalRepository
# from agent.db.repositories.messages import MessageRepository
# from agent.db.repositories.users import UserRepository

router = APIRouter()


@router.post("/coach", response_model=TelexResponse)
async def telex_webhook(payload: TelexRequest):
    user_msg = payload.message or ""

    if not user_msg.strip():
        reply = "Hi! I'm your AI Coaching Agent. What are you working on today?"
    else:
        reply = run_gemini(user_msg)

    return TelexResponse(message=reply)


@router.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": PROJECT_NAME,
        "description": "Smart Multi-Modal Coaching Agent (Gemini-enabled).",
        "capabilities": [
            "learning", "planning", "motivation", "progress_tracking",
            "multimodal", "coding", "communication", "personal_growth"
        ],
        "a2a_version": "1.0.0",
        "endpoints": {"rpc": "/rpc", "status": "/status"}
    }


@router.post("/rpc", response_model=JsonRpcResponse)
async def rpc_entry(
    req: Request,
    x_agent_api_key: Optional[str] = Header(None),
    # redis_: redis.Redis = Depends(get_redis),
    # goal_repo: GoalRepository = get_repository(GoalRepository),
    # message_repo: MessageRepository = get_repository(MessageRepository),
    # user_repo: UserRepository = get_repository(UserRepository),
) -> JsonRpcResponse:
    try:
        body = await req.json()
        rpc = JsonRpcRequest(**body)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON-RPC: {e}"
        ) from e

    if rpc.method == "tasks/send":
        return await handle_task_send(rpc)  # , redis_, message_repo, user_repo
    elif rpc.method == "message/send":
        return await handle_message_send(rpc)  # , goal_repo, message_repo, user_repo
    elif rpc.method == "progress/update":
        return await handle_progress_update(rpc)  # , redis_
    else:
        return JsonRpcResponse(id=rpc.id, error={"code": -32601, "message": "Method not found"})


async def handle_task_send(
    rpc: JsonRpcRequest,
    # redis_: redis.Redis,
    # message_repo: MessageRepository,
    # user_repo: UserRepository,
) -> JsonRpcResponse:
    params = rpc.params or {}
    task = params.get("task", {})

    parts = task.get("parts", [])
    text_inputs = []
    for p in parts:
        if isinstance(p, dict) and p.get("text"):
            text_inputs.append(p["text"])
        elif isinstance(p, str):
            text_inputs.append(p)

    user_text = " ".join(text_inputs).strip() or task.get("title", "")

    reply = run_gemini(user_text)

    session_key = f"session:{params.get('context_id') or str(uuid.uuid4())}"
    # if redis_:
    #     try:
    #         await redis_.set(session_key, json.dumps({"last_user": user_text, "last_reply": reply}), ex=7200)
    #     except Exception:
    #         pass

    result = {
        "task_id": task.get("id", str(uuid.uuid4())),
        "status": "completed",
        "parts": [{"type": "text", "text": reply}],
        "context_id": params.get("context_id")
    }

    return JsonRpcResponse(id=rpc.id, result=result)


async def handle_message_send(
    rpc: JsonRpcRequest,
    # goal_repo: GoalRepository,
    # message_repo: MessageRepository,
    # user_repo: UserRepository,
) -> JsonRpcResponse:
    params = rpc.params or {}
    message = params.get("message")

    if isinstance(message, dict):
        text = message.get("text")
    else:
        text = message

    if not text:
        return JsonRpcResponse(id=rpc.id, error={"code": -32602, "message": "Missing message text"})

    if text.lower().startswith(("create goal:", "new goal:")):
        title = text.split(":", 1)[1].strip()
        sender = params.get("sender")
        # user = await user_repo.create_user(str(sender)) if sender else None
        # g = await goal_repo.create_goal(user.id if user else None, title=title)
        return JsonRpcResponse(id=rpc.id, result={"message": f"Goal created: {title}"})

    reply = run_gemini(text)

    return JsonRpcResponse(id=rpc.id, result={"message": {"text": reply}})


async def handle_progress_update(
    rpc: JsonRpcRequest,
    # redis_: redis.Redis,
) -> JsonRpcResponse:
    params = rpc.params or {}
    # if redis_:
    #     await redis_.rpush("progress_updates", json.dumps(params))

    return JsonRpcResponse(id=rpc.id, result={"status": "acknowledged"})


def push_log_to_telex(channel_id: str, content: str):
    if not channel_id:
        return
    url = f"{TELEX_LOG_BASE}/{channel_id}.txt"
    headers = {}
    if AGENT_API_KEY:
        headers["X-AGENT-API-KEY"] = AGENT_API_KEY
    try:
        import requests
        requests.post(url, json={"log": content}, headers=headers, timeout=5)
    except Exception as e:
        logger.debug("Could not push to telex logs. Error: %s", e)
