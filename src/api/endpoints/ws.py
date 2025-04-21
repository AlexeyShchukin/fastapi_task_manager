from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.websockets.manager import manager

router = APIRouter()


@router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(client_id: int, websocket: WebSocket):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id} wrote: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
