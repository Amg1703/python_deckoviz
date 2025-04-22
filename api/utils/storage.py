import os
from google.cloud import storage


def upload_to_gcs(local_path: str, remote_prefix: str) -> str:
    """
    Uploads a file to Google Cloud Storage and makes it public.

    Args:
        local_path: Path to the local file to upload.
        remote_prefix: Folder path in the bucket (e.g., 'personal_painter').

    Returns:
        Public URL of the uploaded blob.
    """ 
    if not local_path:
        raise ValueError("local_path is required.") 
    if not remote_prefix:
        raise ValueError("remote_prefix is required.")
    
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME env var not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    filename = os.path.basename(local_path)
    blob_path = f"{remote_prefix}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    
    # Make the blob publicly accessible
    # blob.make_public()
    
    os.remove(local_path)

    return blob.public_url
