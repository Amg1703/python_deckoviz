"""
This script downloads images from Flickr based on a user-defined search query and saves both the images and their metadata to the local file system.

Dependencies:
    - flickr_api: For interacting with the Flickr API to search for photos.
    - urllib.request: For downloading images from the internet.
    - os: For file and directory operations.
    - json: For handling JSON data to save and load metadata.

Functions:
    - download_images_with_pagination(tags, download_dir, metadata_file, num_photos=1000):
      Downloads images from Flickr based on the specified tags, saves them to the given directory, and appends metadata to the specified JSON file. Handles pagination to fetch multiple pages of results.
      
      Args:
          tags (str): Search tags to filter photos.
          download_dir (str): Directory to save downloaded images.
          metadata_file (str): File path to save metadata in JSON format.
          num_photos (int, optional): Total number of photos to download. Default is 1000.
    
Usage:
    - Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your Flickr API credentials in the `set_keys` function.
    - Run the script, enter a search query when prompted, and specify the directory for saving images and metadata. The script will handle pagination and download up to the specified number of photos.

Error Handling:
    - The script includes error handling for issues retrieving photo data and downloading images. Metadata is saved even if some photos fail to download.
"""

import urllib.request
import os
import json
import flickr_api


# Set Flickr API credentials
flickr_api.set_keys(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")


def download_images_with_pagination(tags, download_dir, metadata_file, num_photos=1000):
    """
    Downloads images from Flickr based on specified tags and saves them to the local file system.
    Metadata about each image is also saved to a JSON file.

    Args:
        tags (str): Search tags to filter photos.
        download_dir (str): Directory to save downloaded images.
        metadata_file (str): File path to save metadata in JSON format.
        num_photos (int, optional): Total number of photos to download. Default is 1000.

    Raises:
        Exception: If there is an issue with downloading images or saving metadata.
    """
    per_page = 500  # Max number of results per request
    pages = (num_photos // per_page) + 1  # Calculate the number of pages required

    os.makedirs(download_dir, exist_ok=True)
    # Load existing metadata if the file exists
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata_list = json.load(f)
    else:
        metadata_list = []
    photos_downloaded = 0  # Counter to track the number of downloaded photos
    # Download images and collect metadata
    for page in range(1, pages + 1):
        if photos_downloaded >= num_photos:
            break  # Stop if we've already downloaded the desired number of photos

        photos = flickr_api.Photo.search(tags=tags, per_page=per_page, page=page)

        for photo in photos:
            if photos_downloaded >= num_photos:
                break  # Stop if we've already downloaded the desired number of photos

            try:
                # Download photo
                url = photo.getPhotoFile()
                file_path = os.path.join(download_dir, f"{photo.id}.jpg")

                # Check if URL is valid
                if url:
                    urllib.request.urlretrieve(url, file_path)
                    print(f"Downloaded {file_path}")

                    # Append metadata
                    metadata = {
                        "id": photo.id,
                        "title": photo.title,
                        "owner": photo.owner.username,
                        "tags": [
                            str(tag) for tag in photo.tags
                        ],  # Convert tags to strings
                        "date_taken": getattr(photo, "dates", {}).get("taken", "N/A"),
                        "url": url,
                    }
                    metadata_list.append(metadata)
                    photos_downloaded += (
                        1  # Increment the counter for downloaded photos
                    )
            except AttributeError as e:
                print(f"Error retrieving data for photo {photo.id}: {e}")
                continue

    # Save updated metadata
    try:
        with open(metadata_file, "w") as f:
            json.dump(metadata_list, f, indent=4)
            print(f"Metadata saved to {metadata_file}")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error saving metadata: {e}")


# Example usage
if __name__ == "__main__":
    query = input("Enter search query: ")
    download_images_with_pagination(
        query, "./flickr_images", "./flickr_images/metadata.json", 5
    )
