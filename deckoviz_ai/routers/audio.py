from genai.assembly_ai import AudioProcessor
from fastapi import APIRouter, HTTPException
from schemas.audio import TranscriptionRequest, TranscriptionResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio from a URL"""
    try:
        logger.info(f"Transcribing audio from URL: {request.audio_url}")
        processor = AudioProcessor()
        result = processor.get_transcript(request.audio_url)
        return {
            "transcript": result,
            "status": "completed",
            "id": request.id,
            "audio_file_path": request.audio_url
        }
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
