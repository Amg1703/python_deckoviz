from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from deckoviz_ai.personal_painter.personal_painter import PersonalPainter
from deckoviz_ai.personal_painter.personal_painter import process_emotion_and_generate_art
from dotenv import load_dotenv
from utils.storage import upload_to_gcs

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
    # Local output directory
    output_dir = os.path.join(os.getcwd(), "output", "personal_painter")
    os.makedirs(output_dir, exist_ok=True)
    painter = PersonalPainter(api_key=api_key, image_dir=output_dir)

    # Generate art
    result = await process_emotion_and_generate_art(painter, req.user_input)
    image_path = result.get("art", {}).get("image_path")
    prompt = result.get("art", {}).get("prompt")
    print(image_path)
    if not image_path:
        raise HTTPException(status_code=400, detail="Image generation failed")

    # Upload generated image and get public URL
    url = upload_to_gcs(image_path, "personal_painter")

    return GenerateResponse(url=url, prompt=prompt)
