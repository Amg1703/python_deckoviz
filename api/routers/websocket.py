# WebSocket router setup: import necessary FastAPI classes and logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
from core.logger import logger

# Initialize router and logger
router = APIRouter()


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

# Function to notify clients in a room with arbitrary JSON payload
async def notify_new_images(room_id: str, payload: dict):
    """
    Broadcast the given JSON payload to all WebSocket clients in the room.
    """
    await manager.broadcast(room_id, payload)


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


