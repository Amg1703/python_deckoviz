from google.cloud import storage
from decouple import config 
from apps.gallery.models import Audio
import boto3

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
    



class AWSStorage:
    """
    AWS Storage class for uploading files to AWS S3.
    """
    def __init__(self) -> None:
        self.client = boto3.client("s3")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") 
        if not self.bucket_name:
            raise ValueError("AWS_BUCKET_NAME env var not set.")
        if not self.region:
            raise ValueError("AWS_REGION env var not set.")
        if not self.access_key:
            raise ValueError("AWS_ACCESS_KEY_ID env var not set.")
        if not self.secret_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY env var not set.")
        
    def _generate_s3_key(self, tenant_id: str, filename: str) -> str:
        """
        Helper to generate the S3 key using tenant_id and filename
        """
        return f"{tenant_id}/{filename}"

    def upload_bytes_to_aws(self, data: bytes, filename: str, tenant_id: str) -> str:
        """
        Uploads in-memory bytes to AWS S3 under a tenant-specific path.
        """
        blob_path = self._generate_s3_key(tenant_id, filename)
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=blob_path,
            Body=data, 
        )
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{blob_path}"

    def upload_file_to_aws(self, file_path: str, tenant_id: str) -> str:
        """
        Uploads a file to AWS S3 under a tenant-specific path.
        """
        filename = os.path.basename(file_path)
        blob_path = self._generate_s3_key(tenant_id, filename)
        self.client.upload_file(file_path, self.bucket_name, blob_path)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{blob_path}"
 