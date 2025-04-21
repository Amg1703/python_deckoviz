from fastapi import APIRouter, Depends, HTTPException, Body
from databases.configs import get_redis_client
from redis import Redis
import json
import asyncio
from .websocket import notify_new_images

router = APIRouter()


@router.post("/image-search/{room_id}")
async def search_images_api(room_id: str, query: dict = Body(...), redis_client: Redis = Depends(get_redis_client)):
    """
    Search for images based on a query and store results in Redis
    
    Args:
        room_id: Unique identifier for the room/session
        query: JSON body containing the search query
        
    Returns:
        dict: Summary of search results
    """
    if not query or "text" not in query:
        raise HTTPException(status_code=400, detail="Query text is required")
    
    search_query = query["text"]
    n_images = query.get("n_images", 10)
    m_collections = query.get("m_collections", 4)
    x_images_in_collection = query.get("x_images_in_collection", 5)
    
    
    # Use integrated search to get images and collections
    results = image_searcher.integrated_search(
        query=search_query,
        n_images=n_images,
        m_collections=m_collections,
        x_images_in_collection=x_images_in_collection
    )
    
    # Store results in Redis with key pattern image_search_<room_id>
    redis_key = f"image_search_{room_id}"
    redis_client.set(redis_key, json.dumps(results))
    
    # Prepare summary response
    summary = {
        "status": "success",
        "query": search_query,
        "images_count": len(results['top_images']),
        "collections_count": len(results['top_collections']),
        "redis_key": redis_key
    }
    
    # Notify clients about new search results
    asyncio.create_task(notify_new_images(room_id))
    
    return summary


@router.get("/image-search/{room_id}")
async def get_image_search_results(room_id: str):
    """
    Retrieve image search results for a specific room from Redis
    
    Args:
        room_id: Unique identifier for the room/session
        
    Returns:
        dict: Image search results including top images and collections
    """
    redis_key = f"image_search_{room_id}"
    
    # Get data from Redis
    redis_data = redis_client.get(redis_key)
    
    if not redis_data:
        raise HTTPException(status_code=404, detail="No search results found for this room")
    
    # Parse JSON data from Redis
    try:
        results = json.loads(redis_data)
        return results
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding search results")

@router.get("/images/{room_id}/{image_name}")
async def get_image(room_id: str, image_name: str):
    room_path = BASE_DIR / room_id
    image_path = room_path / image_name

    if not room_path.exists() or not room_path.is_dir():
        raise HTTPException(status_code=404, detail="Room not found")
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


@router.get("/images/{room_id}", dependencies=[Depends(get_redis_client)])
async def list_images(room_id: str):
    room_path = BASE_DIR / room_id

    if not room_path.exists() or not room_path.is_dir():
        raise HTTPException(status_code=404, detail="Room not found")

    images = []
    for f in room_path.iterdir():
        if f.is_file():
            stats = os.stat(f)
            images.append({
                "name": f.name,
                "timestamp": stats.st_mtime * 1000  # Convert to milliseconds for JS
            })
    
    # Sort images by timestamp, newest first
    images.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"images": images}

