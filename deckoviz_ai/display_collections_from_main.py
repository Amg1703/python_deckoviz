"""
This script displays images based on metadata stored in a JSON file. The images 
are displayed either at specified times or randomly if no specific display time is set. 
The script utilizes the Tkinter library for GUI display, Pillow for image processing, 
and handles errors related to file access and data parsing.

Dependencies:
- os
- json
- random
- tkinter
- Pillow (PIL)
- datetime
- time

Error Handling:
- The script handles common errors such as file not found, JSON decode errors, and 
  unexpected exceptions, printing relevant messages to the console.
"""

import os
import json
import random
import time
import tkinter as tk
from datetime import datetime, timedelta
from PIL import Image, ImageTk


def show_image_for_duration(image_path, duration):
    """
    Displays an image for a specified duration using Tkinter.

    Parameters:
    image_path (str): The file path of the image to be displayed.
    duration (int): The duration in seconds for which the image should be displayed.

    Raises:
    Exception: If the image fails to load or display.
    """
    try:
        root = tk.Tk()
        root.title("Image Display")

        # Load and display the image
        img = Image.open(image_path)
        tk_image = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=tk_image)
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.pack()

        # Close the window after 'duration' seconds
        root.after(duration * 1000, root.destroy)  # duration is in milliseconds

        root.mainloop()
    except Exception as e:
        print(f"Error displaying image {image_path}: {e}")


def display_image(image_data):
    """
    Displays an image based on the provided metadata.

    Parameters:
    image_data (dict): A dictionary containing metadata about the image,
                       including 'title', 'description', 'associated_music',
                       'id', and 'display_duration'.

    Raises:
    FileNotFoundError: If the image file cannot be found.
    Exception: For any other unexpected errors during image display.
    """
    try:
        print(f"Displaying image: {image_data['title']}")
        print(f"Description: {image_data['description']}")
        print(f"Associated Music: {image_data['associated_music']}")

        # Load and display the image file
        file_name = f"{image_data['id']}.png"
        image_path = os.path.join("main", file_name)
        show_image_for_duration(image_path, image_data["display_duration"])
    except FileNotFoundError:
        print(f"Error: Image file '{file_name}' not found.")
    except Exception as err:
        print(
            f"Unexpected error encountered during displaying image '{image_data['title']}': {err}"
        )


def display_images_from_collection(json_file):
    """
    Reads a JSON file containing image metadata and displays images at specified times.

    Parameters:
    json_file (str): The file path of the JSON file containing image metadata.

    Raises:
    FileNotFoundError: If the JSON file cannot be found.
    json.JSONDecodeError: If the JSON file is improperly formatted.
    Exception: For any other unexpected errors during JSON file loading or image display.
    """
    try:
        with open(json_file, "r") as file:
            collection = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: JSON file '{json_file}' is not properly formatted.")
        return
    except Exception as err:
        print(f"Unexpected error occurred while loading JSON file '{json_file}': {err}")
        return

    try:
        images = collection.get("images_id", [])
        if not images:
            print("No images found in the collection.")
            return

        # Convert time_of_display strings to datetime objects for comparison
        for image in images:
            display_time_str = image.get("time_of_display")
            if display_time_str:
                try:
                    image["display_time"] = datetime.strptime(
                        display_time_str, "%H:%M"
                    ).time()
                except ValueError:
                    print(
                        f"Error: Invalid time format for image '{image['title']}'. Expected HH:MM format."
                    )
                    image["display_time"] = None

        while True:
            now = datetime.now().time()

            # Find the images that are scheduled for the current time
            scheduled_images = [
                image for image in images if image.get("display_time") == now
            ]

            if scheduled_images:
                for image in scheduled_images:
                    display_image(image)
            else:
                # If no images are scheduled for the current time, display a random image
                random_image = random.choice(images)
                display_image(random_image)

            # Wait for a short period before checking again (e.g., every 30 seconds)
            time.sleep(30)

    except Exception as err:
        print(f"Unexpected error occurred during image display process: {err}")


if __name__ == "__main__":

    # Collection title goes here
    collection_json = "165.json"
    display_images_from_collection(collection_json)
