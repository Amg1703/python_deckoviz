# app.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import os
from routers import image_search,websocket
from databases.configs import get_redis_client

# Initialize the application
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path("output")  # Base directory for images

# if the directory does not exist, create it
if not BASE_DIR.exists():
    os.makedirs(BASE_DIR)

# Include routers
app.include_router(websocket.router)
app.include_router(image_search.router)

@app.get("/", dependencies=[Depends(get_redis_client)])
async def root():
    return {"message": "Welcome to the Deckoviz Image API. Use /images/{room_id} to list images or /images/{room_id}/{image_name} to get an image."}

