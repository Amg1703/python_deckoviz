# WebSocket router setup: import necessary FastAPI classes and logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body
import logging
from typing import Dict, Set
import uuid
import json

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("WebSocket router initialized")

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        logger.debug(f"Accepting websocket connection for room {room_id}")
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                logger.debug(f"Broadcasting message to room {room_id}")
                try:
                    await connection.send_json(message)
                except:
                    await self.disconnect(connection, room_id)

# Create a singleton instance of the connection manager
manager = ConnectionManager()

@router.websocket("/ws/{room_id}/")  # support trailing slash
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint: echo incoming messages for testing."""
    logger.debug(f"WS connection requested for room {room_id}")
    await manager.connect(websocket, room_id)
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(msg)
    except WebSocketDisconnect:
        logger.debug(f"Client disconnected from room {room_id}")
        manager.disconnect(websocket, room_id)

# Function to notify clients in a room with arbitrary JSON payload
async def notify_new_images(room_id: str, payload: dict):
    """
    Broadcast the given JSON payload to all WebSocket clients in the room.
    """
    await manager.broadcast(room_id, payload)

# HTTP endpoint to trigger a broadcast of arbitrary JSON payload to a room
@router.post("/rooms/{room_id}/notify_image")
async def trigger_notify(room_id: str, payload: dict = Body(...)):
    """
    HTTP endpoint to broadcast the supplied JSON payload to all WebSocket clients in a room.
    """
    await notify_new_images(room_id, payload)
    return {"status": "notified", "room_id": room_id, "payload": payload}

# APIs
@router.post("/rooms")
async def create_room():
    """
    Create a new room for WebSocket connections with a generated UUID.
    
    Returns:
        dict: Room ID and status
    """
    room_id = str(uuid.uuid4())
    logger.debug(f"Creating new room {room_id}")
    manager.active_connections[room_id] = set()
    return {"room_id": room_id, "status": "created"}