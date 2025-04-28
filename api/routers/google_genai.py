from fastapi import APIRouter
# import time
# from google.genai import genai
# from google.genai import types
# import os
# from google.cloud import storage
# from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


# class GenerateVideoRequest(BaseModel):
#     prompt: str
    

# def generate_video(prompt):
#     # Initialize client
#     print('apikey',os.getenv("GEMINI_API_KEY"))
#     client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # read API key from GOOGLE_API_KEY
#     # init storage client
#     storage_client = storage.Client()
#     bucket_name = os.getenv("GCS_BUCKET_NAME")
#     if not bucket_name:
#         raise ValueError("GCS_BUCKET_NAME env var not set.")
#     bucket = storage_client.bucket(bucket_name)
#     video_urls = []

#     # generate a starter image via Imagen
#     imagen = client.models.generate_images(
#         model="imagen-3.0-generate-002",
#         prompt=prompt,
#         config=types.GenerateImagesConfig(
#             aspect_ratio="16:9",
#             number_of_images=1
#         )
#     )
#     image_input = imagen.generated_images[0].image

#     # then generate video from that image
#     operation = client.models.generate_videos(
#         model="veo-2.0-generate-001",
#         prompt=prompt,
#         image=image_input,
#         config=types.GenerateVideosConfig(
#             aspect_ratio="16:9",  # image-to-video flow; person_generation not allowed
#             number_of_videos=1
#         ),
#     )

#     while not operation.done:
#         time.sleep(20)
#         operation = client.operations.get(operation)

#     for n, generated_video in enumerate(operation.response.generated_videos):
#         file_path = f"video{n}.mp4"
#         client.files.download(file=generated_video.video)
#         generated_video.video.save(file_path)
#         # upload to GCS and make public
#         blob = bucket.blob(file_path)
#         blob.upload_from_filename(file_path)
#         # blob.make_public()
#         video_urls.append(blob.public_url)

#     return video_urls, None



# @router.post("/generate-video")
# async def generate_video_route(prompt: GenerateVideoRequest):
#     urls, error = generate_video(prompt.prompt)
#     if error:
#         return {"error": error}
#     return {"video_urls": urls}
