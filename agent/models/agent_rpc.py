from typing import Any, Dict, Optional
from pydantic import BaseModel


class JsonRpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class TelexRequest(BaseModel):
    id: str | None = None
    message: str | None = None
    sender: str | None = None
    channel_id: str | None = None
    workflow_id: str | None = None


class TelexResponse(BaseModel):
    message: str
