"""
This module provides functionality for curating image collections based on metadata search results,
and saving the curated collections with associated metadata to JSON files.

It includes the following features:
- Searching for images based on tags and labels within the metadata.
- Curating a collection of images based on search results.
- Capturing and storing metadata for the curated collection, including title, description, labels,
  and creation date.
- Saving the curated collection's metadata to a JSON file.

Modules Imported:
- json: Used for reading and writing JSON files.
- os: Provides functions to interact with the operating system.
- datetime: Used for capturing the current date and time.
- search_engine_metadata_based: A custom module providing functions for searching
    metadata based on tags and labels.

Functions:
- result_to_collection(metadata_list, result, collection, collection_labels): 
    Adds a specific image's metadata to a collection and updates the collection's labels.
  
- curate_collection(metadata_list, search_results): 
    Curates a collection of images based on search results and their metadata.

- get_collection_title(): 
    Prompts the user to input the title of a collection and returns it.

- get_collection_description(): 
    Prompts the user to input the description of a collection and returns it.

- get_creation_date(): 
    Stores the current date and time as the creation date of a collection and returns it.

- collection_metadata(image_list, labels): 
    Creates and saves a JSON file containing metadata for a curated collection of images.

- main(): 
    The main function that orchestrates the entire process of metadata loading, searching, 
    curating, and saving the collection.
"""

import json
import os
from datetime import datetime
from search_engine_metadata_based import search_labels, search_tags


def result_to_collection(metadata_list, result, collection, collection_labels):
    """
    Adds a specific image's metadata to a collection and updates the collection's labels.

    Args:
        metadata_list (list): A list of dictionaries containing image metadata.
        result (str): The ID of the image to be added to the collection.
        collection (list): The current list of dictionaries representing the
            curated image collection.
        collection_labels (list): The current list of labels associated with the curated collection.

    Returns:
        tuple: A tuple containing:
            - collection (list): The updated list of dictionaries representing the
                curated image collection.
            - collection_labels (list): The updated list of labels
                associated with the curated collection.
    """
    for meta_data in metadata_list:
        if meta_data["id"] == result:
            collection.append(meta_data)
            for label in meta_data["labels"]:
                if label not in collection_labels:
                    collection_labels.append(label)
    return collection, collection_labels


def curate_collection(metadata_list, search_results):
    """
    Curates a collection of images based on search results and their metadata.

    Args:
        metadata_list (list): A list of dictionaries containing image metadata.
        search_results (list): A list of image IDs that match the search criteria.

    Returns:
        tuple: A tuple containing:
            - curated_collection (list): A list of dictionaries representing
                the curated image collection.
            - collection_labels (list): A list of labels associated with the curated collection.

    Raises:
        Exception: If an error occurs during the curation process,
            it will be printed to the console,
                   and the function will return False.
    """
    try:
        curated_collection = []
        collection_labels = []
        for result in search_results:
            curated_collection, collection_labels = result_to_collection(
                metadata_list, result, curated_collection, collection_labels
            )
        return curated_collection, collection_labels
    except Exception as err:
        print("Error encountered during curating collection: ", err)
        return False


def get_collection_title():
    """
    Prompts the user to input the title of a collection and returns it.

    Returns:
        str: The title of the collection.
    """
    title = input("Enter the title of the collection: ")
    return title


def get_collection_description():
    """
    Prompts the user to input the description of a collection and returns it.

    Returns:
        str: The description of the collection.
    """
    description = input("Enter the description of the collection: ")
    return description


def get_creation_date():
    """
    Stores the current date and time as the creation date of a collection and returns it.

    Returns:
        str: The date of creation of the collection in 'YYYY-MM-DD HH:MM:SS' format.
    """
    creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return creation_date


def collection_metadata(image_list, labels):
    """
    Creates and saves a JSON file containing metadata for a curated collection of images.

    Args:
        image_list (list): A list of image IDs to be included in the collection.
        labels (list): A list of labels associated with the images in the collection.

    Returns:
        bool: Returns True if the collection metadata is successfully saved to a JSON file;
              otherwise, returns False if an error occurs.

    Raises:
        Exception: If an error occurs during the creation or saving of the collection metadata,
                   it will be printed to the console, and the function will return False.
    """
    try:

        collection_title = get_collection_title()
        collection_title = collection_title.strip() + ".json"
        collection_desc = get_collection_description()
        collection_doc = get_creation_date()

        collection_metadata = {
            "title": collection_title,
            "images_id": image_list,
            "description": collection_desc,
            "labels": labels,
            "date_of_creation": collection_doc,
        }
        with open(collection_title, "w") as json_file:
            json.dump(collection_metadata, json_file, indent=4)
            print("Collection curated to json")
            return True
    except Exception as err:
        print("Error encountered during saving collection meta_data: ", err)
        return False


def main():
    """
    The main function that orchestrates the process of loading metadata, searching for images
    based on keywords, curating a collection of images, and saving
    the collection's metadata to a JSON file.

    Workflow:
        1. Loads image metadata from a JSON file.
        2. Prompts the user to input a comma-separated list of keywords.
        3. Searches for images in the metadata that match the given tags and labels.
        4. Curates a collection of images based on the search results.
        5. Saves the curated collection's metadata to a JSON file.
        6. Prints the success or failure status of the collection creation.

    Returns:
        None

    Raises:
        Exception: If an error occurs at any step, it will be printed to the console.
    """
    try:
        with open("meta_data.json", "r") as json_file:
            meta_data = json.load(json_file)
        keywords = input("Enter a comma-separated list of keywords: ").split(",")
        tags_results = search_tags(keywords, meta_data)
        search_results = search_labels(
            keywords, meta_data, tags_results, count=len(tags_results)
        )
        curated_collection, collection_labels = curate_collection(
            meta_data, search_results
        )
        status = collection_metadata(curated_collection, collection_labels)
        if status is True:
            print("Collection created succesfully.")
        else:
            print("COllection creation failed.")
    except Exception as err:
        print("Error encountered during saving collection meta_data: ", err)


if __name__ == "__main__":
    main()
