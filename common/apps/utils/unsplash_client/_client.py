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
         
         
        for query in self.search_queries:
            collection_name = query.strip().lower().replace(" ", "_") 

            photo_data = self.fetch_photos(query)  

            if not photo_data:
                logger.info(f"No photos found for query '{query}'.")
                continue 

            for data in photo_data:

                id = data.get("id")
                description = data.get("description")
                alt_description = data.get("alt_description")
                unsplash_url = data.get("urls").get('full')
                local_image_path = data.get("local_image_path")
                bunny_cdn_url = data.get("bunny_cdn_url")
                photographer = data.get("photographer")
                photographer_url = data.get("photographer_url")
                tags = data.get("tags") 
 
                user = User.objects.get(is_superuser=True)

                metadata = {
                        "source":"unsplash",
                        "query":query,"created_by":"system", 
                        "description":description,
                        "alt_description":alt_description,
                        "local_image_path":local_image_path,
                        "bunny_cdn_url":bunny_cdn_url,
                        "created_at":datetime.now().isoformat(),
                        "tags":tags,
                        "urls":data.get("urls"),
                        "photographer":photographer,
                        "photographer_url":photographer_url
                }

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
            
                if Image.objects.filter(image_id=id).exists():
                    image = Image.objects.get(image_id=id)
                else:
                    image = Image.objects.create(
                    external_url=unsplash_url,
                    music=None,
                    image_id=id,
                    uploaded_by=user,
                    view='public',
                    is_active=True
                )
                if not CollectionImage.objects.filter(image=image,collection=collection).exists():
                    collectionimage = CollectionImage.objects.create(
                        collection=collection,
                        image=image, 
                    )
                    # logger.info(collectionimage)  

            # Add a delay between queries to respect API limits
            time.sleep(5)
            