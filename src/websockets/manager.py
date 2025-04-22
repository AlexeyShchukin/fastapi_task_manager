from fastapi.websockets import WebSocket

from src.core.security import decode_token


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, token: str):
        try:
            decode_token(token)
            await websocket.accept()
            self.active_connections.add(websocket)
        except Exception:
            await websocket.close(code=1008)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
