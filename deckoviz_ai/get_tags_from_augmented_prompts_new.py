"""
Script for extracting tags from augmented image descriptions using the OpenAI API.

This script reads augmented prompts from a JSON file, sends each prompt to an OpenAI language model,
and extracts relevant tags related to style, content, and scene information from the responses.
The extracted tags are then saved back into a JSON file, maintaining a dictionary structure where
the keys correspond to the indices of the prompts.

Modules and Functions:
-----------------------
- `get_llm_response(client, system, prompt, model="gpt-3.5-turbo")`:
    Sends a prompt to OpenAI's language model and retrieves the response.
    
- `read_augmented_prompts(filename="augmented_prompts.json")`:
    Reads augmented prompts from a JSON file.
    
- `save_tags_to_json(filename, index, tags)`:
    Saves the extracted tags to a JSON file as part of a dictionary structure.
    
- `extract_tags(client)`:
    Iterates over the augmented prompts, extracts relevant tags using the OpenAI API, and saves them.

Dependencies:
-------------
- `os`: Provides a way of using operating system dependent functionality like file system access.
- `json`: Used for reading from and writing to JSON files.
- `openai`: The OpenAI Python client library for interacting with the OpenAI API.

Usage:
------
1. Ensure the OpenAI API key is available and correctly set.
2. The script will read augmented prompts from 'augmented_prompts.json'.
3. It will send each prompt to the OpenAI model and extract tags from the response.
4. The extracted tags will be saved into 'tags.json'.

Error Handling:
---------------
- The script includes error handling for file operations, JSON parsing, and API responses.
- In case of an invalid LLM response, the script falls back to an empty list of tags.
"""

import os
import json
from openai import OpenAI


def get_llm_response(client, system, prompt, model="gpt-3.5-turbo"):
    """
    Sends a prompt to OpenAI's language model and retrieves the response.

    Parameters:
        client (OpenAI): The OpenAI client object.
        system (str): The system message to define the role or behavior of the assistant.
        prompt (str): The user prompt to generate the response.
        model (str): The language model to use (default is "gpt-3.5-turbo").

    Returns:
        tuple: A tuple containing the response message (str) and the number of tokens used (int).
    """
    try:
        messages = [{"role": "system", "content": system}] + [
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1,
        )

        response_message = response.choices[0].message.content
        response_tokens = response.usage.total_tokens

        return response_message, response_tokens
    except Exception as err:
        print(f"Exception encountered during LLM response retrieval: {err}")
        return "", 0


def read_augmented_prompts(filename="augmented_prompts.json"):
    """
    Reads augmented prompts from a JSON file.

    Parameters:
        filename (str): The name of the file to read the data from.

    Returns:
        dict: A dictionary containing the augmented prompts.
    """
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        else:
            print(f"File '{filename}' not found.")
            return {}

    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{filename}'.")
        return {}

    except Exception as err:
        print(f"Exception encountered while reading augmented prompts: {err}")
        return {}


def save_tags_to_json(filename, index, tags):
    """
    Saves the extracted tags to a JSON file as part of a dictionary.
    If the file already exists, it reads the existing data,
    and saves the new tags with the same index as the key.
    If the file does not exist or is empty, it creates a new dictionary.

    Parameters:
        filename (str): The name of the file to save the data.
        index (int): The index of the prompt from which the tags were extracted.
        tags (list): The list of tags extracted from the prompt.
    """
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    existing_data = json.load(file)
                    if not isinstance(existing_data, dict):
                        print(
                            "Warning: Existing data is not a dictionary, it will be replaced."
                        )
                        existing_data = {}
                except json.JSONDecodeError:
                    print(
                        "Warning: File is empty or corrupted, starting with a new dictionary."
                    )
                    existing_data = {}
        else:
            existing_data = {}

        # Add the new tags to the dictionary with the given index
        existing_data[index] = tags

        # Save the updated dictionary back to the file
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)

    except Exception as err:
        print("Exception encountered during saving tags to JSON:", err)


def extract_tags(client):
    """
    Extracts relevant tags from augmented prompts using the OpenAI API.

    Parameters:
        client (OpenAI): The OpenAI client object.
    """
    augmented_prompts = read_augmented_prompts("augmented_prompts.json")

    system_prompt = r"""Extract relevant tags from the given description of an image.
        Look for style, content, and scene information.
        Provide your extracted tags in the format of a Python list.
        Your reply should consist of only the list tags and nothing else,
        in case no tags are extracted from the the description, or it isn’t a description,
        reply with an empty tags list only.
        
        **Example 1:**
        
        A photograph of a serene lake with a family of ducks swimming on its calm surface,
        surrounded by lush green trees and a clear blue sky.
        
        Reply:
        [
            "Serene",
            "Lake",
            "Family",
            "Ducks",
            "Swimming",
            "Trees",
            "Green",
            "Blue",
            "Sky",
            "Nature",
            "Scenic"
        ]
        
        
        **Example 2:**
        
        A vibrant painting of a busy city street with cars, buses, and pedestrians moving about,
        while a large skyscraper looms in the background.
        
        Reply:
        [
            "Vibrant",
            "City",
            "Street",
            "Cars",
            "Buses",
            "Pedestrians",
            "Skyscraper",
            "Urban",
            "Architecture",
            "Movement"
        ]
        **Example 3:**
        
        A black and white photograph of an old, abandoned factory with broken windows,
        rusted pipes, and a crumbling facade, set against a backdrop of a desolate urban landscape.
        
        Reply:
        [
            "Black and White",
            "Abandoned",
            "Factory",
            "Broken",
            "Windows",
            "Rusted",
            "Pipes",
            "Crumbling",
            "Urban",
            "Landscape",
            "Decay"
        ]
        
        """

    for index, prompt in augmented_prompts.items():
        llm_response, _ = get_llm_response(client, system_prompt, prompt)
        # The response should be a list of tags
        try:
            tags = eval(llm_response.strip())
        except Exception as err:
            print("Exception encountered processing llm response:", err)
            tags = []  # Fallback in case the LLM response is not a proper list

        print(f"Tags for prompt {index}: ", tags)
        save_tags_to_json("tags.json", index, tags)


if __name__ == "__main__":
    client = OpenAI(
        api_key="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"
    )
    extract_tags(client)
