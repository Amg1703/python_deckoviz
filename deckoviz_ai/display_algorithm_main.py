"""
This script handles the display of images based on metadata stored in a JSON file.
Images are displayed in a shuffled order, with a user-defined or default display duration.
The script uses Tkinter for the GUI display and Pillow for image handling.

Dependencies:
- os
- json
- random
- tkinter
- Pillow (PIL)
- time

Error Handling:
- The script includes basic error handling for user input, image display, 
  and JSON file processing, ensuring the program continues running in case of errors.
"""

import os
import json
import random
import tkinter as tk
from PIL import Image, ImageTk
import time


def show_image_for_duration(image_path, duration):
    """
    Displays an image for a specified duration using Tkinter.

    Parameters:
    image_path (str): The file path of the image to be displayed.
    duration (int): The duration in seconds for which the image should be displayed.

    Note:
    No exception handling is implemented within this function. Ensure the image path is valid.
    """
    root = tk.Tk()
    root.title("Image Display")

    # Load and display the image
    img = Image.open(image_path)
    tk_image = ImageTk.PhotoImage(img)
    label = tk.Label(root, image=tk_image)

    label.pack()

    # Close the window after 'duration' seconds
    root.after(duration * 1000, root.destroy)  # duration is in milliseconds

    root.mainloop()


def display_image(image_data, duration):
    """
    Displays an image based on provided metadata and duration.

    Parameters:
    image_data (dict): A dictionary containing metadata about the image,
                       including 'title', 'description', 'tags', 'labels',
                       'associated_music', and 'id'.
    duration (int): The duration in seconds for which the image should be displayed.

    Raises:
    Exception: For any unexpected errors during image display, the error is caught,
               logged, and the program continues with the next image.
    """
    try:
        print(f"Displaying image: {image_data['title']}")
        print(f"Description: {image_data['description']}")
        print(f"Tags: {', '.join(image_data['tags'])}")
        print(f"Labels: {', '.join(image_data['labels'])}")
        print(f"Associated Music: {image_data['associated_music']}")

        # Load and display the image file
        file_name = f"{image_data['id']}.png"
        image_path = os.path.join("main", file_name)
        show_image_for_duration(image_path, duration)
    except Exception as err:
        print("Error encountered during displaying image: ", err)
        print("Continuing to next image.")


def get_display_duration():
    """
    Prompts the user for a display duration in seconds.

    Returns:
    int: The display duration in seconds. Defaults to 1800 seconds (30 minutes)
         if the user input is invalid.

    Raises:
    Exception: If an error occurs during input conversion, the error is caught,
               and a default value is returned.
    """
    try:
        duration = int(input("Enter display duration in seconds, defaults to 1800s: "))
        return duration
    except Exception as err:
        print("Error encountered during getting duration: ", err)
        print("Defaulting to 30 mins (1800s) of display period.")
        return 1800


def display_images_from_main(json_file):
    """
    Reads a JSON file containing image metadata and displays images in a shuffled order.

    Parameters:
    json_file (str): The file path of the JSON file containing image metadata.

    Raises:
    Exception: Any errors during JSON file processing or image display are caught,
               allowing the program to continue running.
    """
    try:
        with open(json_file, "r") as file:
            images = json.load(file)

        duration = get_display_duration()
        random.shuffle(images)  # Shuffle the images randomly

        # Display images with the defined duration
        for image in images:
            display_image(image, duration)
    except Exception as err:
        print("Error occurred during reading JSON or processing the same: ", err)


# Example usage:
if __name__ == "__main__":
    # main bucket metadata file
    json_file = "meta_data.json"
    display_images_from_main(json_file)
