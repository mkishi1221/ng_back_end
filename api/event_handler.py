from datetime import datetime
import hashlib
from typing import Dict, Tuple
from pymitter import EventEmitter
from starlette.websockets import WebSocket

from api.models.user_repository.repository import UserRepository

emitter = EventEmitter(wildcard=True)

class User:

    def __init__(self, name: str, project: str, project_id: str):
        self.name = name
        self.project = project
        self.project_id = project_id

class ConnectionManager:
    active_connections: Dict[str, Tuple[User, WebSocket]]

    def __init__(self):
        ConnectionManager.active_connections = {}

    async def connect(self, websocket: WebSocket, name: str, project: str):
        await websocket.accept()
        identifier = hashlib.md5(
            f"{websocket.client.host}{websocket.client.port}{int(datetime.timestamp(datetime.now()))}".encode()
        ).hexdigest()
        project_id = UserRepository.init_user(name, project)
        ConnectionManager.active_connections.update({identifier: (User(name, project, project_id), websocket)})
        await websocket.send_json({"type": "id", "content": identifier})
        emitter.emit("generate_names", identifier) # generate names and send to client

    @staticmethod
    def get_user(identifier: str) -> User:
        return ConnectionManager.active_connections[identifier][0]

    def disconnect(self, websocket: WebSocket):
        socket_to_remove = list(self.active_connections.values()).index(websocket)
        if socket_to_remove:
            self.active_connections.pop(socket_to_remove)

    async def send(self, message, type: str, identifier: str):
        await self.active_connections[identifier][1].send_json(
            {"type": type, "content": message}
        )

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection[1].send_text(message)
