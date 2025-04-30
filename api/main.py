# app.py
from fastapi import FastAPI, Depends
import logging
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
import os
import sys

# Ensure debug logs for all modules (including WebSocket router)
logging.basicConfig(level=logging.DEBUG)

# Ensure project root (parent of api) is on PYTHONPATH so deckoviz_ai is importable
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from routers import image_search,websocket, collections,google_genai,rooms
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

# Include routers
app.include_router(image_search.router)
app.include_router(collections.router)
app.include_router(websocket.router)
app.include_router(google_genai.router)
app.include_router(rooms.router)


@app.get("/", dependencies=[Depends(get_redis_client)])
async def root():
    return {"message": "Welcome to the Deckoviz API."}
