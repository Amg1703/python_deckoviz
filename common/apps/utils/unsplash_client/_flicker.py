"""
This script downloads images from Flickr based on a user-defined search query and saves both the images and their metadata to the local file system.

Dependencies:
    - flickr_api: For interacting with the Flickr API to search for photos.
    - urllib.request: For downloading images from the internet.
    - os: For file and directory operations.
    - json: For handling JSON data to save and load metadata.

Functions:
    - scrape_flickr(tags, download_dir, metadata_file, num_photos=1000):
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

# import urllib.request
# import os
# import json
# import flickr_api


# def scrape_flickr(num_photos=1000,search_query=[]):
#     """
#     Downloads images from Flickr based on specified tags and saves them to the local file system.
#     Metadata about each image is also saved to a JSON file.

#     Args:
#         tags (str): Search tags to filter photos.
#         download_dir (str): Directory to save downloaded images.
#         metadata_file (str): File path to save metadata in JSON format.
#         num_photos (int, optional): Total number of photos to download. Default is 1000.

#     Raises:
#         Exception: If there is an issue with downloading images or saving metadata.
#     """
#     per_page = 500  # Max number of results per request
#     pages = (num_photos // per_page) + 1  # Calculate the number of pages required

#     for query in search_query:
#         for page in range(pages):
#             photos = flickr_api.Photo.search(tags=query, per_page=per_page, page=page)
#             with open(f'flickr_{query}_{page}.json', "w") as f:
#                 json.dump(photos, f)
        
#     return True