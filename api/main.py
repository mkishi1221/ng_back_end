from typing import Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.security import HTTPBearer

from api.models.keyword import Keyword
from .event_handler import emitter, ConnectionManager
import asyncio

from .routes import words_collector

token_auth_scheme = HTTPBearer()
app = FastAPI()
app.include_router(words_collector.router)
manager = ConnectionManager()


@emitter.on("new_words")
def send_names(keywords: List[Keyword], identifier: str):
    loop = asyncio.get_event_loop()
    loop.create_task(manager.send({"words": keywords}, identifier))


@app.websocket("/ws")
async def name_distributor(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while 1:
            await websocket.send_text(
                "keepalive"
            )  # keep the websocket connection alive
            await asyncio.sleep(30)
    except:
        manager.disconnect(websocket)
