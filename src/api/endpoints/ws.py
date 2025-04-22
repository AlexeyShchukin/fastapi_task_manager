import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status

from src.core.security import decode_token
from src.loggers.loggers import logger
from src.websockets.manager import manager

ws_router = APIRouter()


@ws_router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(client_id: int, websocket: WebSocket):
    token = websocket.headers.get('Authorization')
    if token:
        token = token.split(" ")[1]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    payload = decode_token(token)

    await manager.connect(websocket, token)

    try:
        while True:
            data = await websocket.receive_text()
            log_entry = {
                "event": "message_received",
                "client_id": client_id,
                "message": data,
            }
            logger.info(json.dumps(log_entry))
            await manager.broadcast(f"Client {client_id} wrote: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
