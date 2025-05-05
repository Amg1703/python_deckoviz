"""
Unsplash to Bunny.net/GCS Image Uploader (Cron Job)

This script runs as a cron job (every hour) to:
1. Fetch photos from the Unsplash API based on configured search queries
2. Upload images directly to Bunny.net CDN or Google Cloud Storage without local storage
3. Save comprehensive metadata as JSON

Modules:
    - requests: For making HTTP requests to the Unsplash API and Bunny.net CDN
    - json: For handling JSON data for metadata
    - os: For environment variables and minimal file operations
    - dotenv: For loading environment variables from a .env file
    - google.cloud.storage: For Google Cloud Storage operations
    - base64: For encoding/decoding base64 data (unused in current implementation but available)

Environment Variables:
    - UNSPLASH_ACCESS_KEY: API key for Unsplash
    - BUNNY_ACCESS_KEY: API key for Bunny.net
    - BUNNY_STORAGE_ZONE: Your storage zone name in Bunny.net
    - BUNNY_REGION: Region for Bunny.net (optional)
    - GCS_BUCKET_NAME: Google Cloud Storage bucket name
    - SEARCH_QUERIES: Comma-separated list of search queries to use
    - COLLECTIONS_FOLDER: Base folder for organizing collections
    - METADATA_FILE: Path to the JSON metadata file
    - STORAGE_PROVIDER: "bunny" or "gcs" to select storage provider
"""
 
import base64  # Added for base64 encoding/decoding if needed
import json
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import django
import logging

logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps 
from django.contrib.auth import get_user_model
from django.conf import settings

apps.populate(settings.INSTALLED_APPS)

Collection = apps.get_model('gallery', 'Collection')
Image = apps.get_model('gallery', 'Image')
CollectionImage = apps.get_model('gallery', 'CollectionImage')
Price = apps.get_model('marketplace', 'Price')
User = get_user_model()

from django.db import transaction

try:
    from google.cloud import storage
except ImportError:
    # GCS module not installed, will use Bunny.net only
    pass

# Load environment variables
load_dotenv()

class UnsplashClient:
    """
    Manager class that handles fetching from Unsplash and uploading to either
    Bunny.net CDN or Google Cloud Storage.
    """
    
    def __init__(self, search_queries=[]):
        # Load Unsplash credentials
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.unsplash_access_key:
            raise ValueError("UNSPLASH_ACCESS_KEY not found in environment variables")
        
        # Load storage configuration
        self.storage_provider = os.getenv("STORAGE_PROVIDER", "bunny")
        
        # Load Bunny.net credentials if needed
        if self.storage_provider == "bunny":
            self.bunny_access_key = os.getenv("BUNNY_ACCESS_KEY")
            self.bunny_storage_zone = os.getenv("BUNNY_STORAGE_ZONE")
            self.bunny_region = os.getenv("BUNNY_REGION", "")
            
            if not self.bunny_access_key or not self.bunny_storage_zone:
                raise ValueError("BUNNY_ACCESS_KEY or BUNNY_STORAGE_ZONE not found in environment variables")
            
            # Set up Bunny.net base URL
            self.bunny_base_url = "storage.bunnycdn.com"
            if self.bunny_region:
                self.bunny_base_url = f"{self.bunny_region}.{self.bunny_base_url}"
        
        # GCS configuration is loaded when needed in the respective methods
        
        # Metadata storage configuration
        self.metadata_file = os.getenv("METADATA_FILE", "photos_metadata.json")
        self.collections_folder = os.getenv("COLLECTIONS_FOLDER", "unsplash_collections")
        
        # Load search queries
        self.search_queries = search_queries
        
        # Load request parameters
        self.per_page = int(os.getenv("IMAGES_PER_QUERY", "10"))
        self.orientation = os.getenv("ORIENTATION", "landscape")
        
        # Load existing metadata if available
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        """
        Loads existing metadata from the file if it exists.
        
        Returns:
            dict: The loaded metadata or an empty dictionary.
        """
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            return {"collections": {}, "last_run": None, "total_images": 0}
        except Exception as e:
            print(f"Error loading metadata: {e}. Creating new metadata.")
            return {"collections": {}, "last_run": None, "total_images": 0}

    def _save_metadata(self):
        """
        Saves the current metadata to the file.
        """
        try:
            # Update last run timestamp
            self.metadata["last_run"] = datetime.now().isoformat()
            
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=4)
            print(f"Metadata saved to {self.metadata_file}.")
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def fetch_photos(self, query):
        """
        Fetches photos from Unsplash API based on the search query.

        Args:
            query (str): The search query for photos.

        Returns:
            dict or None: JSON response from Unsplash API if successful, otherwise None.
        """
        url = f"https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "client_id": self.unsplash_access_key,
            "per_page": self.per_page,
            "orientation": self.orientation
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching photos for query '{query}': {e}")
            return None

    def upload_to_bunny(self, image_data, storage_path):
        """
        Uploads image data directly to Bunny.net CDN without saving locally.

        Args:
            image_data (bytes): The binary image data.
            storage_path (str): Path where the file should be stored on Bunny.net.

        Returns:
            tuple: (bool, str) - Success status and CDN URL or error message.
        """
        url = f"https://{self.bunny_base_url}/{self.bunny_storage_zone}/{storage_path}"
        headers = {
            "AccessKey": self.bunny_access_key,
            "Content-Type": "application/octet-stream",
            "accept": "application/json"
        }
        
        try:
            response = requests.put(url, headers=headers, data=image_data)
            response.raise_for_status()
            
            # Log response for debugging
            print(f"Bunny.net upload response: {response.status_code}")
            
            # Construct the CDN URL
            cdn_url = f"https://{self.bunny_storage_zone}.b-cdn.net/{storage_path}"
            return True, cdn_url
        except Exception as e:
            return False, str(e)

    def upload_bytes_to_gcs(self, data, filename, remote_prefix):
        """
        Uploads in-memory bytes to GCS and makes it public.
        
        Args:
            data (bytes): The binary image data.
            filename (str): Filename to use in the bucket.
            remote_prefix (str): Folder path in the bucket.
            
        Returns:
            str: Public URL of the uploaded blob.
        """
        try:
            bucket_name = os.getenv("GCS_BUCKET_NAME")
            if not bucket_name:
                raise ValueError("GCS_BUCKET_NAME env var not set.")
                
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob_path = f"{remote_prefix}/{filename}"
            blob = bucket.blob(blob_path)
            blob.upload_from_string(data, content_type="image/jpeg")
            # blob.make_public()  # Uncomment if you want to make the image public
            
            return blob.public_url
        except Exception as e:
            raise ValueError(f"Error uploading to GCS: {str(e)}")
            
    def upload_to_gcs(self, image_data, storage_path):
        """
        Uploads image data to Google Cloud Storage without saving locally.

        Args:
            image_data (bytes): The binary image data.
            storage_path (str): Path where the file should be stored in GCS.

        Returns:
            tuple: (bool, str) - Success status and public URL or error message.
        """
        try:
            filename = storage_path.split("/")[-1]
            remote_prefix = "/".join(storage_path.split("/")[:-1])
            
            url = self.upload_bytes_to_gcs(image_data, filename, remote_prefix)
            return True, url
        except Exception as e:
            return False, str(e)

    def process_photo_data(self, photo_data, collection_name):
        """
        Process photo data and upload images from a given collection
        
        Args:
            photo_data (dict): Photo data returned from the Unsplash API
            collection_name (str): Name of the collection to associate images with
            
        Returns:
            tuple: (int, list) - Number of photos uploaded and list of processed image data
        """
        if not photo_data or "results" not in photo_data:
            logger.warning(f"No valid photo data found for collection '{collection_name}'")
            return 0
            
        if not photo_data["results"]:
            logger.info(f"No photos found for collection '{collection_name}'.")
            return 0
            
        # Initialize collection in metadata if not exists
        if collection_name not in self.metadata["collections"]:
            self.metadata["collections"][collection_name] = []
            
        # Track existing IDs to avoid duplicates
        existing_ids = {item["id"] for item in self.metadata["collections"][collection_name]}
        
        success_count = 0
        for photo in photo_data:
            # Skip if already in metadata
            if photo["id"] in existing_ids:
                logger.info(f"Skipping duplicate photo {photo['id']}")
                continue
                
            # Prepare metadata entry
            entry = {
                "id": photo["id"],
                "description": photo.get("description", "No description"),
                "alt_description": photo.get("alt_description", "No alt description"),
                "unsplash_url": photo["urls"]["full"],
                "storage_url": None,  # Will be updated after upload
                "photographer": photo.get("user", {}).get("name", "Unknown"),
                "photographer_url": photo.get("user", {}).get("links", {}).get("html", ""),
                "tags": [tag.get("title", "") for tag in photo.get("tags", [])],
                "collection": collection_name,
                "added_date": datetime.now().isoformat()
            }
            
            # Get image data
            try:
                # Use a smaller image size for efficiency
                image_url = photo["urls"]["regular"]
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_data = image_response.content
                
                # Store the image format (jpeg or png)
                content_type = image_response.headers.get('Content-Type', 'image/jpeg')
            except requests.exceptions.RequestException as e:
                logger.info(f"Error downloading image {photo['id']}: {e}")
                continue
            
            # Generate filename and paths
            filename = f"{photo['id']}.jpg"
            storage_path = f"{self.collections_folder}/{collection_name}/{filename}"
            remote_prefix = f"{self.collections_folder}/{collection_name}"
            
            # Upload image to selected storage
            if self.storage_provider == "bunny":
                success, result = self.upload_to_bunny(image_data, storage_path)
            else:  # gcs
                try:
                    # Use your upload_bytes_to_gcs function directly
                    result = self.upload_bytes_to_gcs(image_data, filename, remote_prefix)
                    success = True
                except Exception as e:
                    success = False
                    result = str(e)
                
            if success:
                logger.info(f"Uploaded {photo['id']} to {self.storage_provider} at {result}")
                entry["storage_url"] = result
                self.metadata["collections"][collection_name].append(entry)
                success_count += 1
            else:
                logger.info(f"Failed to upload {photo['id']}: {result}")
                
            # Add a small delay to avoid rate limits
            time.sleep(0.5)
            
        # Update total count
        self.metadata["total_images"] = sum(len(items) for items in self.metadata["collections"].values())
        
        # Return both the success count and the list of processed images (with storage URLs)
        processed_images = [img for img in self.metadata["collections"][collection_name] 
                          if img.get("storage_url") is not None]
        
        return success_count, processed_images

    def run(self):
        """
        Main function to run the uploader process for all configured queries.
        """
        logger.info(f"Starting Unsplash to {self.storage_provider} uploader job at {datetime.now().isoformat()}")
        logger.info(f"Using {len(self.search_queries)} search queries: {', '.join(self.search_queries)}")
        
        total_uploaded = 0
        collections_created = []
         
        for query in self.search_queries:
            collection_name = query.strip().lower().replace(" ", "_") 

            # photo_data = self.fetch_photos(query)
            photo_data = [
                    {
                        "id": "IicyiaPYGGI",
                        "description": None,
                        "alt_description": "orange flowers",
                        "unsplash_url": "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHwxfHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/IicyiaPYGGI.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Henry Be",
                        "photographer_url": "https://unsplash.com/@henry_be",
                        "tags": []
                    },
                    {
                        "id": "EwKXn5CapA4",
                        "description": "Finding my roots",
                        "alt_description": "sun light passing through green leafed tree",
                        "unsplash_url": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHwyfHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/EwKXn5CapA4.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Jeremy Bishop",
                        "photographer_url": "https://unsplash.com/@jeremybishop",
                        "tags": []
                    },
                    {
                        "id": "d4feocYfzAM",
                        "description": None,
                        "alt_description": "bed of orange flowers",
                        "unsplash_url": "https://images.unsplash.com/photo-1529419412599-7bb870e11810?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHwzfHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/d4feocYfzAM.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Damiano Baschiera",
                        "photographer_url": "https://unsplash.com/@damiano_baschiera",
                        "tags": []
                    },
                    {
                        "id": "1h2Pg97SXfA",
                        "description": None,
                        "alt_description": "calm sky during daytime",
                        "unsplash_url": "https://images.unsplash.com/photo-1530908295418-a12e326966ba?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw0fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/1h2Pg97SXfA.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Kenrick Mills",
                        "photographer_url": "https://unsplash.com/@kenrickmills",
                        "tags": []
                    },
                    {
                        "id": "Rfflri94rs8",
                        "description": "Conifer sapling",
                        "alt_description": "selective photography of green leaf plant",
                        "unsplash_url": "https://images.unsplash.com/photo-1421789665209-c9b2a435e3dc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw1fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/Rfflri94rs8.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Matthew Smith",
                        "photographer_url": "https://unsplash.com/@whale",
                        "tags": []
                    },
                    {
                        "id": "igX2deuD9lc",
                        "description": "You can help and support me via my description (Paypal) !\n\nInstagram : @clvmentm\nFacebook Page : www.facebook.com/CMReflections/\n\nIf you wish to buy it in full quality, email me on clementmreflections@gmail.com.",
                        "alt_description": "photo of pine trees",
                        "unsplash_url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw2fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/igX2deuD9lc.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Cl\u00e9ment M.",
                        "photographer_url": "https://unsplash.com/@cmreflections",
                        "tags": []
                    },
                    {
                        "id": "dXYE1d08BiY",
                        "description": "Pooling Water",
                        "alt_description": "green leaf with water drops",
                        "unsplash_url": "https://images.unsplash.com/photo-1495584816685-4bdbf1b5057e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw3fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/dXYE1d08BiY.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Aaron Burden",
                        "photographer_url": "https://unsplash.com/@aaronburden",
                        "tags": []
                    },
                    {
                        "id": "FIKD9t5_5zQ",
                        "description": None,
                        "alt_description": "white clouds during daytime",
                        "unsplash_url": "https://images.unsplash.com/photo-1428908728789-d2de25dbd4e2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw4fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/FIKD9t5_5zQ.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Dominik Schr\u00f6der",
                        "photographer_url": "https://unsplash.com/@wirhabenzeit",
                        "tags": []
                    },
                    {
                        "id": "Kp9z6zcUfGw",
                        "description": None,
                        "alt_description": "macro photography of drop of water on top of green plant",
                        "unsplash_url": "https://images.unsplash.com/photo-1471879832106-c7ab9e0cee23?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHw5fHxuYXR1cmV8ZW58MHx8fHwxNzQ2NDQ0MTk1fDA&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/Kp9z6zcUfGw.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Aaron Burden",
                        "photographer_url": "https://unsplash.com/@aaronburden",
                        "tags": []
                    },
                    {
                        "id": "kqJfP-lrl-8",
                        "description": "I used 5 tiers of glass to create this layered effect and placed cuts of branches in between each layer.",
                        "alt_description": "white flowering plant artwork",
                        "unsplash_url": "https://images.unsplash.com/photo-1515096788709-a3cf4ce0a4a6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDcxMzZ8MHwxfHNlYXJjaHwxMHx8bmF0dXJlfGVufDB8fHx8MTc0NjQ0NDE5NXww&ixlib=rb-4.0.3&q=85",
                        "local_image_path": "images/kqJfP-lrl-8.jpg",
                        "bunny_cdn_url": None,
                        "photographer": "Evie S.",
                        "photographer_url": "https://unsplash.com/@evieshaffer",
                        "tags": []
                    }
              ]
            
            print(collection_name)

            for data in photo_data:
                id = data.get("id")
                description = data.get("description")
                alt_description = data.get("alt_description")
                unsplash_url = data.get("unsplash_url")
                local_image_path = data.get("local_image_path")
                bunny_cdn_url = data.get("bunny_cdn_url")
                photographer = data.get("photographer")
                photographer_url = data.get("photographer_url")
                tags = data.get("tags")

                print(id,description,alt_description,unsplash_url,local_image_path,bunny_cdn_url,photographer,photographer_url,tags)
                
                user = User.objects.get(is_superuser=True)
                metadata = {"source":"unsplash","query":query,"created_by":"system","created_at":datetime.now().isoformat(),"tags":tags,"photographer":photographer,"photographer_url":photographer_url}
                meta_notes = json.dumps(metadata)

                collections = Collection.objects.filter(name=collection_name)
                if collections.exists():
                    collection = collections.first()
                else:
                    collection = Collection.objects.create(
                        name=collection_name,
                        user=user,
                        meta_notes=meta_notes,
                        type="meta",
                        view="public",
                        display_time=5,
                        is_active=True,
                        metadata=metadata
                    )
                image = Image.objects.create(
                    external_url=unsplash_url,
                    music=None,
                    image_id=id,
                    uploaded_by=user,
                    view='public',
                    is_active=True
                )
                collectionimage = CollectionImage.objects.create(
                    collection=collection,
                    image=image, 
                )
            print(collectionimage)  

            # Add a delay between queries to respect API limits
            time.sleep(1)
             