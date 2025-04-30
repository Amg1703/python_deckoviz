from celery import shared_task 
from .models import Audio
from .ai_client import AIClient
from .storage import Storage
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_audio():
    print("Fetching audios to process")
    audios = Audio.objects.filter(transcript_status='processing', is_active=True)
    print(f"Found {audios.count()} audios to process")

    for audio in audios:
        try:        
            client = AIClient()
            result = client.transcribe_audio(audio.audio.url)
            print(f"Transcribing audio {audio.id}: {result}")

            # Upload transcript to GCS
            storage = Storage()
            upload_response = storage.upload_transcript(result['transcript'], audio.id)
            print(f"Transcript uploaded to {upload_response}")

            # Update audio model
            if result['success']:
                audio.transcript = result['transcript']
                audio.transcript_url = upload_response
                audio.transcript_status = 'completed'
                audio.save()
            else:
                print(f"Failed to transcribe audio {audio.id}: {result['error']}")
        except Exception as e:
            print(f"Error processing audio {audio.id}: {str(e)}")