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
    
    def transcribe_audio(self, audio_url: str, analyze: bool = False) -> Dict[str, Any]:
        """
        Transcribe audio from a URL via the decoviz_ai service.
        
        Args:
            audio_url: URL of the audio file
            analyze: Whether to analyze the transcript for insights
            
        Returns:
            Dict containing transcription result, insights (if analyze=True), or error information
        """
        endpoint = f"{self.base_url}/audio/transcribe"
        payload = {"audio_url": audio_url, "analyze": analyze}
        
        try:
            logger.info(f"Sending transcription request for URL: {audio_url} with analyze={analyze}")
            response = requests.post(endpoint, json=payload, timeout=120)  # Increased timeout for analysis
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully transcribed audio - ID: {result.get('id')}")
                
                response_data = {
                    "success": True,
                    "transcript": result.get("transcript", ""),
                    "id": result.get("id"),
                    "status": result.get("status", ""),
                }
                
                # Include insights if they were requested and are available
                if analyze and result.get("insights"):
                    response_data["insights"] = result.get("insights")
                    logger.info("Transcript analysis completed successfully")
                
                return response_data
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
    
    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze a transcript to extract insights.
        
        Args:
            transcript: The transcript text to analyze
            
        Returns:
            Dict containing analysis results or error information
        """
        endpoint = f"{self.base_url}/audio/analyze"
        payload = {"transcript": transcript}
        
        try:
            logger.info(f"Sending transcript analysis request for {len(transcript)} characters")
            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully analyzed transcript")
                return {
                    "success": True,
                    "insights": result.get("insights", {}),
                }
            else:
                error_msg = f"Analysis failed - Status code: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            return self._handle_request_exception(e, "transcript analysis")

    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 40) -> Dict[str, Any]:
        """
        Generate a summary of the provided text.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of summary in tokens
            min_length: Minimum length of summary in tokens
            
        Returns:
            Dict containing summary or error information
        """
        endpoint = f"{self.base_url}/audio/summarize"
        payload = {"text": text, "max_length": max_length, "min_length": min_length}
        
        try:
            logger.info(f"Sending summarization request for {len(text)} characters")
            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully generated summary")
                return {
                    "success": True,
                    "summary": result.get("summary", "")
                }
            else:
                error_msg = f"Summarization failed - Status code: {response.status_code}, Response: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            return self._handle_request_exception(e, "summarization")
    
    def health_check(self) -> bool:
        """Check if the AI service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
