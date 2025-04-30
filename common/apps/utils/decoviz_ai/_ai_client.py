import requests
import logging
from django.conf import settings
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AIClient:
    """Client for communicating with the decoviz_ai service"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the AI client.
        
        Args:
            base_url: Base URL for the decoviz_ai service. If not provided,
                    uses DECOVIZ_AI_URL from settings or defaults to http://decoviz_ai:8001
        """
        self.base_url = base_url or getattr(settings, 'DECKOVIZ_AI_URL', 'http://deckoviz_ai:8001')
        logger.info(f"Initialized AI client with base URL: {self.base_url}")
    
    def _handle_request_exception(self, e: Exception, service_name: str) -> Dict[str, Any]:
        """Handle exceptions from API requests"""
        error_msg = f"Error connecting to {service_name} service: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    
    def transcribe_audio(self, audio_url: str) -> Dict[str, Any]:
        """
        Transcribe audio from a URL via the decoviz_ai service.
        
        Args:
            audio_url: URL of the audio file
            
        Returns:
            Dict containing transcription result or error information
        """
        endpoint = f"{self.base_url}/audio/transcribe"
        payload = {"audio_url": audio_url}
        
        try:
            logger.info(f"Sending transcription request for URL: {audio_url}")
            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully transcribed audio - ID: {result.get('id')}")
                return {
                    "success": True,
                    "transcript": result.get("transcript", ""),
                    "id": result.get("id"),
                    "status": result.get("status", ""),
                }
            else:
                error_msg = f"Transcription failed - Status code: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False, 
                    "error": error_msg,
                    "status": "failed"
                }
                
        except Exception as e:
            return self._handle_request_exception(e, "transcription")
    
    def health_check(self) -> bool:
        """Check if the AI service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
