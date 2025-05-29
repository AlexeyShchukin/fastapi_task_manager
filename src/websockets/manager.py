from fastapi.websockets import WebSocket

from src.loggers.loggers import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str = None):
        if client_id and client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        else:
            for cid, conns in list(self.active_connections.items()):
                if websocket in conns:
                    conns.remove(websocket)
                    if not conns:
                        del self.active_connections[cid]
                    break

    async def broadcast(self, message: str, client_id: str = None):
        recipients = set()

        if client_id:
            recipients.update(self.active_connections.get(client_id, set()))

        recipients.update(self.active_connections.get("*", set()))

        for connection in list(recipients):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                self.disconnect(connection)




manager = ConnectionManager()
