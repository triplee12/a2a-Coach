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
    try:
        user_msg = payload.message or ""

        if not user_msg.strip():
            reply = "Hi! I'm your AI Coaching Agent. What are you working on today?"
        else:
            reply = await run_gemini(user_msg)

        if not reply.strip():
            push_log_to_telex(payload.channel_id, f"User: {user_msg}")
            push_log_to_telex(payload.channel_id, f"Agent: {reply}")

        return TelexResponse(message=reply)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
        "endpoints": {
            "rpc": "/rpc",
            "status": "/status",
            "telex": "/coach"
        }
    }


@router.post("/rpc", response_model=JsonRpcResponse)
async def rpc_entry(
    req: Request,
) -> JsonRpcResponse:
    try:
        body = await req.json()
        rpc = JsonRpcRequest(**body)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON-RPC: {e}"
        ) from e

    if rpc.method == "tasks/send":
        return await handle_task_send(rpc)
    elif rpc.method == "message/send":
        return await handle_message_send(rpc)
    elif rpc.method == "progress/update":
        return await handle_progress_update(rpc)
    else:
        return JsonRpcResponse(id=rpc.id, error={"code": -32601, "message": "Method not found"})


async def handle_task_send(rpc: JsonRpcRequest) -> JsonRpcResponse:
    try:
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

        reply = await run_gemini(user_text)

        result = {
            "task_id": task.get("id", str(uuid.uuid4())),
            "status": "completed",
            "parts": [{"type": "text", "text": reply}],
            "context_id": params.get("context_id")
        }

        return JsonRpcResponse(id=rpc.id, result=result)
    except Exception as e:
        logger.exception(e)
        return JsonRpcResponse(id=rpc.id, error={"code": -32602, "message": "Internal Server Error"})


async def handle_message_send(rpc: JsonRpcRequest) -> JsonRpcResponse:
    try:
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
            return JsonRpcResponse(id=rpc.id, result={"message": f"Goal created: {title}"})

        reply = await run_gemini(text)

        return JsonRpcResponse(id=rpc.id, result={"message": {"text": reply}})
    except Exception as e:
        logger.exception(e)
        return JsonRpcResponse(id=rpc.id, error={"code": -32602, "message": "Internal Server Error"})


async def handle_progress_update(rpc: JsonRpcRequest) -> JsonRpcResponse:
    try:
        params = rpc.params or {}
        # if redis_:
        #     await redis_.rpush("progress_updates", json.dumps(params))

        return JsonRpcResponse(id=rpc.id, result={"status": "acknowledged"})
    except Exception as e:
        logger.exception(e)
        return JsonRpcResponse(id=rpc.id, error={"code": -32602, "message": "Internal Server Error"})


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
