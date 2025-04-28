from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
import json
from routers.websocket import manager
from databases.configs import get_redis_client

router = APIRouter(
    prefix="/collections",
    tags=["collections"]
)

# class CollectionPayload(BaseModel):
#     data: Dict[str, Any]

# class BatchRequest(BaseModel):
#     space_mb: float


# # Redis client for queue operations 
# redis_client = get_redis_client()


# @router.post("/{room_id}")
# async def send_collection(room_id: str, payload: CollectionPayload):
#     """
#     Send a collection payload to all clients connected to the given room.

#     room_id: identifier for the room
#     payload: dict payload representing the collection
#     """
#     # Push to Redis list and trim to max 20 entries
#     key = f"queue:{room_id}"
#     await redis_client.rpush(key, json.dumps(payload.data))
#     await redis_client.ltrim(key, -20, -1)
#     length = await redis_client.llen(key)
#     return {"status": "queued", "queue_length": length}


# @router.post("/{room_id}/batch")
# async def send_batch(room_id: str, request: BatchRequest):
#     """
#     Send next batch of queued collections fitting into available space_mb
#     """
#     key = f"queue:{room_id}"
#     items = await redis_client.lrange(key, 0, -1)
#     sent, total = [], 0.0
#     for s in items:
#         itm = json.loads(s)
#         size = itm.get("size_mb", 0)
#         if total + size <= request.space_mb:
#             sent.append(itm); total += size
#         else:
#             break
#     if sent:
#         await redis_client.ltrim(key, len(sent), -1)
#     for itm in sent:
#         msg = {"type": "collection_update", "data": itm}
#         await manager.broadcast(room_id, msg)
#     remaining = await redis_client.llen(key)
#     return {"status": "batch_sent", "sent_count": len(sent), "remaining": remaining}
