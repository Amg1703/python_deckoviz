from pydantic import BaseModel
from typing import Optional

class TranscriptionRequest(BaseModel):
    audio_url: str
    id: Optional[str] = None

    
class TranscriptionResponse(BaseModel):
    transcript: str
    status: str

