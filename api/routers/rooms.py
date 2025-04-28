from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
import json
from routers.websocket import manager, notify_new_images
from databases.configs import get_redis_client
from  core.logger import logger
import uuid
import threading
import httpx
import time

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)

class BatchRequest(BaseModel):
    space_mb: float
    images: list



@router.post("/")
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


# HTTP endpoint to trigger a broadcast of arbitrary JSON payload to a room
@router.post("/{room_id}/notify")
async def trigger_notify(room_id: str, payload: dict = Body(...)):
    """
    HTTP endpoint to broadcast the supplied JSON payload to all WebSocket clients in a room.
    """
    await notify_new_images(room_id, payload)
    return {"status": "notified", "room_id": room_id, "payload": payload}


@router.post("/{room_id}/batch")
async def send_batch(
    room_id: str,
    request: BatchRequest,
    redis_client=Depends(get_redis_client)
):
    """
    Send next batch of queued collections fitting into available space_mb
    """
    print(request)
    key = f"queue:{room_id}"
    items = redis_client.lrange(key, 0, -1)
    # print(room_id)
    # print(request.images)
    sent, total = [], 0.0
    for s in items:
        itm = json.loads(s)
        size = itm.get("size_mb", 0)
        if total + size <= request.space_mb:
            sent.append(itm); total += size
        else:
            break
    if sent:
        redis_client.ltrim(key, len(sent), -1)
    for itm in sent:
        msg = {"type": "collection_update", "data": itm}
        await manager.broadcast(room_id, msg)
    remaining = redis_client.llen(key)
    return {"status": "batch_sent", "sent_count": len(sent), "remaining": remaining}
    # if there are remaining items, schedule a retry in 10 minutes
    if remaining > 0:
        def retry():
            time.sleep(600)
            try:
                httpx.post(f"http://localhost:8080/rooms/{room_id}/batch", json={"space_mb": request.space_mb})
            except Exception:
                pass
        threading.Thread(target=retry, daemon=True).start()
