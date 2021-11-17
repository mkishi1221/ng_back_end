from datetime import datetime
import hashlib
from typing import Dict
from pymitter import EventEmitter
from starlette.websockets import WebSocket

emitter = EventEmitter(wildcard=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        identifier = hashlib.md5(
            f"{websocket.client.host}{websocket.client.port}{int(datetime.timestamp(datetime.now()))}".encode()
        ).hexdigest()
        self.active_connections.update({identifier: websocket})
        await websocket.send_text(identifier)

    def disconnect(self, websocket: WebSocket):
        socket_to_remove = ""
        for connection in self.active_connections:
            if self.active_connections[connection] == websocket:
                socket_to_remove = connection
        self.active_connections.pop(socket_to_remove)

    async def send(self, message, identifier: str):
        await self.active_connections[identifier].send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)