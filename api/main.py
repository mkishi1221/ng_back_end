from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from api.models.user_repository.mutations.user_preferences import (
    UserPreferenceMutations,
)
from api.routes import (
    algorithm_collector,
    blacklist_collector,
    settings,
    whitelist_collector,
    words_collector,
    tld_collector,
)
from .event_handler import ConnectionManager
import asyncio


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://identitytobrand.com:3000",
]

token_auth_scheme = HTTPBearer()
app = FastAPI(title="identitytobrand lofi api", version="0.0.1")
app.include_router(words_collector.router)
app.include_router(algorithm_collector.router)
app.include_router(blacklist_collector.router)
app.include_router(whitelist_collector.router)
app.include_router(tld_collector.router)
app.include_router(settings.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()


@app.websocket("/ws")
async def name_distributor(websocket: WebSocket, name: str, project: str):
    await manager.connect(websocket, name, project)
    await UserPreferenceMutations.set_last_project(name, project)
    try:
        while 1:
            await websocket.send_json(
                {"type": "keepalive"}
            )  # keep the websocket connection alive
            await asyncio.sleep(30)
    except:
        manager.disconnect(websocket)
