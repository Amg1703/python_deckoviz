from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from deckoviz_ai.personal_painter.personal_painter import PersonalPainter, process_emotion_and_generate_art
from dotenv import load_dotenv
from utils.storage import upload_bytes_to_gcs

load_dotenv()

router = APIRouter(
    prefix="/image-generator",
    tags=["image_generation"]
)

class GenerateRequest(BaseModel):
    user_input: str

class GenerateResponse(BaseModel):
    url: str
    prompt: str

@router.post("/", response_model=GenerateResponse)
async def generate_image(req: GenerateRequest):
    # Initialize Personal Painter
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="STABILITY_API_KEY is not set")
    # # Local output directory
    # output_dir = os.path.join(os.getcwd(), "output", "personal_painter")
    # os.makedirs(output_dir, exist_ok=True)
    # painter = PersonalPainter(api_key=api_key, image_dir=output_dir)

    # Generate art and get image bytes
    result = await process_emotion_and_generate_art(painter, req.user_input)
    art = result.get("art", {})
    image_bytes = art.get("image_bytes")
    filename = art.get("filename")
    prompt = art.get("prompt")
    if not image_bytes or not filename:
        raise HTTPException(status_code=400, detail="Image generation failed")

    # Upload bytes directly to GCS
    url = upload_bytes_to_gcs(image_bytes, filename, "personal_painter")
    return GenerateResponse(url=url, prompt=prompt)
