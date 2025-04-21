import os
import requests
import json
from openai import OpenAI


def read_augmented_prompts(filename="augmented_prompts.json"):
    """
    Reads augmented prompts from a JSON file.

    Args:
        filename (str): The name of the file containing the augmented prompts.

    Returns:
        dict or bool: The dictionary of augmented prompts, or False if an error occurs.
    """
    with open(filename, "r") as file:
        augmented_prompts = json.load(file)
    return augmented_prompts


def get_image_response(client, user_prompt, image_size="1792x1024", style="vivid"):
    """
    Requests an image generation from a client using specified parameters.

    Args:
        client: The client object used to make the image generation request.
        user_prompt (str): The prompt or description for generating the image.
        image_size (str): The dimensions of the image to generate (e.g., "1024x1024").
        style (str): The style of the image generation ("natural" or "vivid").

    Returns:
        dict or bool: The response from the image generation request, formatted as a URL,
                     or False if an error occurs.

    If an error occurs during the image generation request, the function catches the
    exception, prints an error message, and returns False.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=user_prompt,
            n=1,
            size=image_size,
            quality="hd",
            style=style,
            response_format="url",
        )
        return response
    except Exception as error:
        print("Error in getting image response: {}\n ".format(error))
        return False


def ext_img_from_response(response):
    """
    Extracts images from a response object containing image URLs.

    Args:
        response: The response object containing image URLs.

    Returns:
        list or bool: A list of image content in bytes format, or False if an error occurs.

    This function extracts image URLs from the provided response object, downloads
    each image, and returns a list of image content in bytes format. If an error occurs
    during the extraction or download process, it catches the exception, prints an error
    message, and returns False.
    """
    try:
        image_urls = [datum.url for datum in response.data]  # extract URLs
        images = [requests.get(url).content for url in image_urls]  # download images
        return images
    except Exception as error:
        print("Error in getting image response: {}\n ".format(error))
        return False


def save_images_to_dir(image, image_dir, index):
    """
    Saves images to a directory with specified filenames.

    Args:
        images (list): List of image content in bytes format.
        image_dir (str): Directory path where images will be saved.
        prompt_no (int): Number identifying the prompt.

    Returns:
        bool: True if images are successfully saved, False otherwise.

    This function creates filenames for each image variation based on the prompt number,
    saves each image to the specified directory, and prints the filepath for each saved image.
    If an error occurs during the saving process, it catches the exception, prints an error
    message, and returns False.
    """
    try:
        image = image[0]
        image_name = f"{index}.png"
        filepath = os.path.join(image_dir, image_name)
        with open(filepath, "wb") as image_file:  # open the file
            image_file.write(image)  # write the image to the file
            print("Image saved to: ", filepath)
        return True
    except Exception as error:
        print("Error in saving image response: {}\n ".format(error))
        return False


def gen_images(client):
    """
    Generates images based on augmented prompts and saves them to a directory.

    Args:
        client: The client object used to make image generation requests.

    This function reads augmented prompts from a JSON file, generates images using the OpenAI API,
    extracts the images from the response, and saves them to a directory. It handles errors in each
    step and prints relevant error messages if any occur.
    """

    image_dir = os.path.join(os.curdir, "dalle_gen_images")
    augmented_prompts = read_augmented_prompts("augmented_prompts.json")
    counter = 0
    for index, prompt in augmented_prompts.items():
        if counter > 1:
            break
        image_response = get_image_response(client, prompt)
        ext_image = ext_img_from_response(image_response)
        save_images_to_dir(ext_image, image_dir, index)
        counter += 1


if __name__ == "__main__":
    client = OpenAI(
        api_key="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"
    )
    gen_images(client)
