from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException

from src.api.dependencies.permission_dependency import permission_required
from src.api.dependencies.user_dependency import get_user_service, get_current_user
from src.services.permission_service import verify_ownership, has_permission
from src.services.user_service import UserService
from src.websockets.manager import manager

ws_router = APIRouter()

@ws_router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(
        client_id: UUID,
        websocket: WebSocket,
        user_service: Annotated[UserService, Depends(get_user_service)]
):
    token_header = websocket.headers.get("Authorization")
    if not token_header or not token_header.lower().startswith("bearer "):
        await websocket.close(code=1008)
        return
    token = token_header.split(" ", 1)[1]

    try:
        user = await get_current_user(token=token, user_service=user_service)
    except HTTPException:
        await websocket.close(code=1008)
        return

    try:
        user = await permission_required("task", "read", allow_own=True)(user)
        verify_ownership(user, client_id)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await manager.connect(websocket, str(client_id))

    if has_permission(user.permission_names, "task", "read", "any"):
        await manager.connect(websocket, "*")

    try:
        while True:
            msg = await websocket.receive_text()
            await manager.broadcast(f"[{client_id}] {msg}", client_id=str(client_id))
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(client_id))
        if has_permission(user.permission_names, "task", "read", "any"):
            manager.disconnect(websocket, "*")

