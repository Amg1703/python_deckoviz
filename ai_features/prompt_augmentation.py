"""
This script is designed to augment simple text prompts into richly detailed, highly descriptive versions using OpenAI's language models.

## Functionality:

1. **get_llm_response**: Sends a prompt to OpenAI's language model and retrieves the augmented response along with the token count.
2. **augment_prompt**: Uses the `get_llm_response` function to generate a detailed, evocative version of a given prompt.
3. **save_to_json**: Saves the augmented prompts to a JSON file. If the file exists, the script appends new prompts to the existing ones while ensuring the file remains valid.
4. **read_prompts_from_json**: Reads prompts from a specified JSON file and returns them as a list.
5. **augmentation**: The main function that reads prompts, generates their augmented versions, and saves them to a file.

## Error Handling and Robustness:

- The script includes comprehensive error handling to manage issues such as file not found, JSON parsing errors, and unexpected API failures.
- The `save_to_json` function is robust, checking the existing file's integrity before appending new data.
- If a file is corrupted or contains invalid data, the script will notify the user and attempt to continue with a fresh data structure.

## Dependencies:

- `os`: Used for file handling and checking file existence.
- `json`: For reading and writing JSON data.
- `openai`: OpenAI Python client to interact with OpenAI's language models.

## Usage:

The script is intended to be run directly, where it will read a set of prompts from `prompts.json`, augment them using OpenAI's models, and then save the results to `augmented_prompts.json`.

"""

import os
import json
from openai import OpenAI


def get_llm_response(client, system, prompt="Proceeding:", model="gpt-3.5-turbo"):
    """
    Communicates with the OpenAI API to generate a response based on the provided prompt.

    Parameters:
        client (OpenAI): The OpenAI client object.
        system (str): The system message to define the role or behavior of the assistant.
        prompt (str): The user prompt to generate the augmented prompt (default is "Proceeding:").
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
    except Exception as e:
        print(f"Error in get_llm_response: {e}")
        return None, 0


def augment_prompt(client, system, prompt):
    """
    Augments a given prompt using the specified system instructions.

    Parameters:
        client (OpenAI): The OpenAI client object.
        system (str): The system message for generating the augmented prompt.
        prompt (str): The user prompt to be augmented.

    Returns:
        str: The augmented prompt.
    """
    try:
        llm_response, llm_tokens = get_llm_response(
            client, system, prompt=prompt, model="gpt-4o-mini"
        )
        return llm_response
    except Exception as e:
        print(f"Error in augment_prompt: {e}")
        return None


def save_to_json(filename, prompt):
    """
    Saves the given prompt to a JSON file as part of a dictionary.
    If the file already exists, it reads the existing data, finds the last index,
    and saves the new prompt with the next index. If the file does not exist or is empty,
    the index starts from 1.

    Parameters:
        filename (str): The name of the file to save the data.
        prompt (str): The augmented prompt to save.
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

        # Determine the next index
        if existing_data:
            next_index = max(map(int, existing_data.keys())) + 1
        else:
            next_index = 1

        # Add the new prompt to the dictionary with the next index
        existing_data[next_index] = prompt

        # Save the updated dictionary back to the file
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)

    except Exception as err:
        print("Exception encountered during saving prompt to JSON:", err)


def read_prompts_from_json(filename="prompts.json"):
    """
    Reads prompts from a JSON file.

    Parameters:
        filename (str): The name of the file to read the prompts from (default is "prompts.json").

    Returns:
        list: A list of prompts read from the file.
    """
    try:
        with open(filename, "r") as file:
            prompts = json.load(file)
        return prompts
    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file {filename} is not in a valid JSON format.")
        return []


def augmentation(client):
    """
    Augments a list of prompts by generating detailed and evocative versions using the OpenAI API.

    Parameters:
        client (OpenAI): The OpenAI client object.
    """
    initial_prompts = read_prompts_from_json("prompts.json")

    if not initial_prompts:
        print("No prompts found to augment.")
        return

    system_prompt = """Your task is to take simple prompts and transform them into richly detailed,

                        highly descriptive, and evocative versions. Every output you generate must be an augmented,
                        elaborated version of the original prompt, focusing on hyperrealism, emotional depth, and profound imagery.
                        You should emphasize vivid descriptions, intricate details, and a strong sense of atmosphere in every response.
                        Always output the augmented version of the prompt and nothing else. Include various elements such as sensory
                        descriptions, metaphors, symbolism, and evocative language.
                        Examples:
                        1.	Input Prompt: A lone figure silhouetted against a sunset.
                        Your Output: 
                        A lone figure stands on a rugged cliff, silhouetted against a breathtaking sunset
                        that paints the sky with an explosion of colors—vibrant oranges, deep purples, and soft pinks blend seamlessly.
                        The figure’s form melds with the ethereal hues of twilight, their silhouette both distinct and ephemeral,
                        as if they are a part of the sky itself. Below, a vast ocean reflects the dying light, each wave a molten mirror
                        of the heavens. The air is thick with the scent of salt and the quiet murmur of the waves, evoking a sense of
                        profound peace and unity. The scene symbolizes the profound interconnectedness of existence, where the boundary
                        between self and universe blurs in the fading light, inviting contemplation on the mysteries of life.
                        2.	Input Prompt: A radiant forest bathed in sunlight.
                        Your output: 
                        A radiant forest, ancient and alive, stretches out as far as the eye can see. Sunlight,
                        filtered through the dense canopy of emerald leaves, bathes the forest floor in a golden glow, creating a
                        mosaic of light and shadow. The air is thick with the earthy scent of moss and the soft hum of life—each rustle
                        of leaves, each distant bird call, a whisper from an ancient world. The trees, towering and majestic, are draped
                        in vines and ferns, their bark etched with the passage of time. A gentle breeze stirs the leaves, sending shafts
                        of light dancing through the mist that clings to the ground, creating an almost otherworldly atmosphere. The
                        viewer is drawn into this realm of enchantment, where every detail—from the delicate dew on a spider’s web to the
                        vibrant green of the moss-covered stones—tells a story of a world untouched by time, a sanctuary for the spirits
                        of the earth.
                        Instructions:
                        •	For every prompt you receive, apply this level of detail and augmentation.
                        •	Always produce an output that is a richly enhanced version of the prompt and nothing else.
                        •	Focus on creating a highly immersive, vivid, and emotive experience through your descriptions.
                        •	Remember our output should strictly only consist of the augmented prompt only, absolutely nothing else.
                        """

    counter = 1
    for prompt in initial_prompts:
        augmented_prompt = augment_prompt(client, system_prompt, prompt)
        if augmented_prompt:
            print(f"Augmented prompt {counter}: ", augmented_prompt)
            save_to_json("augmented_prompts.json", augmented_prompt)
        else:
            print(f"Skipping prompt {counter} due to error.")
        counter += 1


if __name__ == "__main__":
    try:
        client = OpenAI(
            api_key="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"
        )
        augmentation(client)
    except Exception as e:
        print(f"Error in the main execution: {e}")
