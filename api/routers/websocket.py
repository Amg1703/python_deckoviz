# WebSocket router setup: import necessary FastAPI classes and logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.logger import logger
from utils.websocket_manager import manager

# Initialize router and logger
router = APIRouter()


# # Function to notify clients in a room with arbitrary JSON payload
async def notify_new_images(room_id: str, payload: dict):
    """
    Broadcast the given JSON payload to all WebSocket clients in the room.
    """
    await manager.broadcast(room_id, payload)


# @router.websocket("/ws/{room_id}/")  # support trailing slash
# async def websocket_endpoint(websocket: WebSocket, room_id: str, client_type: str = "generic"):
#     """WebSocket endpoint: echo incoming messages for testing."""
#     logger.debug(f"WS connection requested for room {room_id} (generic client)")
#     await manager.connect(websocket, room_id)
#     try:
#         while True:
#             msg = await websocket.receive_text()
#             # Create a message packet that includes metadata
#             message = {
#                 "type": "message",
#                 "content": msg,
#                 "sender": client_type,
#                 "timestamp": import_time().time()
#             }
#             # Broadcast to all clients in the room
#             await manager.broadcast(room_id, message, exclude_sender=websocket)
#             # Echo back to sender
#             await websocket.send_text(msg)
#     except WebSocketDisconnect:
#         logger.debug(f"Client disconnected from room {room_id}")
#         manager.disconnect(websocket)
 