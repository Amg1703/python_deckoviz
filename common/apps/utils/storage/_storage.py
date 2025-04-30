from google.cloud import storage
from decouple import config 
from apps.gallery.models import Audio


class Storage:
    def __init__(self):
        self.bucket_name = config("GCS_BUCKET_NAME")
        self.client = storage.Client()

    def upload_transcript(self, text, audio_id):
        """
        Upload a transcript file to Google Cloud Storage.
        
        Args:
            text: Text content to upload
            audio_id: ID of the audio
            
        Returns:
            url: URL of the uploaded transcript(string)

        Response URL Format:
            transcripts/{audio_id}/transcript.txt

        Raises:
            ValueError: If audio_id is not provided
            ValueError: If text is not provided
            ValueError: If audio not found
        """
        if not audio_id:
            raise ValueError("Audio ID is required")
        if not text:
            raise ValueError("Text is required")
        try:
            audio = Audio.objects.get(id=audio_id)
        except Audio.DoesNotExist:
            raise ValueError("Audio not found.")
        
        blob_name = f"transcripts/{audio.id}/transcript.txt"
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(text)
        return blob.public_url 
    