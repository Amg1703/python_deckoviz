from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict

from routers.websocket import manager

router = APIRouter(
    prefix="/collections",
    tags=["collections"]
)

class CollectionPayload(BaseModel):
    data: Dict[str, Any]

@router.post("/{room_id}")
async def send_collection(room_id: str, payload: CollectionPayload):
    """
    Send a collection payload to all clients connected to the given room.

    room_id: identifier for the room
    payload: dict payload representing the collection
    """
    message = {"type": "collection_update", "data": payload.data}
    await manager.broadcast(room_id, message)
    return {"status": "sent", "room_id": room_id}
