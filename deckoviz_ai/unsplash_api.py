"""
This script fetches photos from the Unsplash API based on a user-provided search query,
and then saves both the photo metadata and images to the local file system.

Modules:
    - requests: For making HTTP requests to the Unsplash API and downloading images.
    - json: For handling JSON data to save and load photo metadata.
    - os: For interacting with the file system, including directory creation and file path management.

Functions:
    - fetch_photos(query, access_key): Fetches photos from Unsplash API using the provided search query and access key.
    - save_metadata(photo_data, meta_file): Saves the metadata of fetched photos to a JSON file.
    - save_images(photo_data, image_dir): Downloads and saves images to a specified directory.
    - main(): Orchestrates the process of fetching photos, saving metadata, and saving images. Prompts user for search query and manages API access key.

Usage:
    - Replace "Your access key" in the `main` function with your Unsplash API access key.
    - Run the script, enter a search query when prompted, and the script will download the images and metadata to the specified directories.

Error Handling:
    - Includes basic error handling for API request failures and file I/O operations.
"""

import json
import os
import requests


# Function to fetch photos from Unsplash API
def fetch_photos(query, access_key):
    """
    Fetches photos from Unsplash API based on the search query.

    Args:
        query (str): The search query for photos.
        access_key (str): Unsplash API access key.

    Returns:
        dict or None: JSON response from Unsplash API if successful, otherwise None.
    """
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={access_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching photos: {e}")
        return None


# Function to save metadata to a JSON file
def save_metadata(photo_data, meta_file):
    """
    Saves photo metadata to a JSON file.

    Args:
        photo_data (dict): The photo data fetched from Unsplash API.
        meta_file (str): The path to the metadata file.
    """
    try:
        # Ensure the directory exists
        meta_dir = os.path.dirname(meta_file)
        os.makedirs(meta_dir, exist_ok=True)

        if os.path.exists(meta_file):
            with open(meta_file, "r") as f:
                metadata = json.load(f)
        else:
            metadata = []

        for photo in photo_data["results"]:
            metadata.append(
                {
                    "id": photo["id"],
                    "description": photo.get("description", "No description"),
                    "url": photo["urls"]["full"],
                    "image_path": f"images/{photo['id']}.jpg",
                }
            )

        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to {meta_file}.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error saving metadata: {e}")


# Function to save images to the local system
def save_images(photo_data, image_dir):
    """
    Saves images to the local system from the given photo data.

    Args:
        photo_data (dict): The photo data fetched from Unsplash API.
        image_dir (str): The directory to save images to.
    """
    os.makedirs(image_dir, exist_ok=True)

    for photo in photo_data["results"]:
        image_url = photo["urls"]["full"]
        image_path = os.path.join(image_dir, f"{photo['id']}.jpg")
        try:
            img_data = requests.get(image_url).content
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"Saved image {photo['id']} to {image_path}.")
        except requests.exceptions.RequestException as e:
            print(f"Error saving image {photo['id']}: {e}")


# Main function to run the script
def main():
    """
    Main function to execute the script: fetch photos, save metadata, and save images.
    """
    access_key = "Your access key"
    query = input("Enter search query: ")

    photo_data = fetch_photos(query, access_key)
    if photo_data:
        save_metadata(photo_data, r"Unsplash_images/image_metadata.json")
        save_images(photo_data, "Unsplash_images/")
        print("Images and metadata saved.")
    else:
        print("No data found or error occurred.")


if __name__ == "__main__":
    main()
