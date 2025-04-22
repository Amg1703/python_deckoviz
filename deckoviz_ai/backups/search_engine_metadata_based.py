"""
This module provides functions for searching and retrieving image metadata 
based on labels and tags. It allows for the search of images by their associated 
labels or tags within a metadata list and prints the matching results in a 
structured JSON format.

Functions:
    - search_labels(labels, metadata_list, search_results=[], count=0)
    - search_tags(tags, metadata_list)
    - print_matching_data(meta_data, search_results)
    - main()
"""

import os
import json


def search_labels(labels, metadata_list, search_results=[], count=0):
    """
    Searches for image metadata entries that match the provided labels.

    Args:
        labels (list): A list of labels to search for within the metadata.
        metadata_list (list): A list of dictionaries containing image metadata.
        search_results (list, optional): A list to store the IDs of matching images.
        Defaults to an empty list.
        count (int, optional): Counter for the number of matching images found. Defaults to 0.

    Returns:
        list|bool: A list of matching image IDs if found; otherwise, returns False.

    Raises:
        Exception: If an error occurs during the search process, it will be printed to the console.
    """
    try:
        for image_entry in metadata_list:
            for label in labels:
                if label in image_entry["labels"]:
                    if image_entry["id"] not in search_results:
                        search_results.append(image_entry["id"])
                        count += 1
        if count != 0:
            return search_results
        else:
            print("No images found that match the search labels.")
            return False
    except Exception as err:
        print("Error encountered during searching through labels: ", err)
        return False


def search_tags(tags, metadata_list):
    """
    Searches for image metadata entries that match the provided tags.

    Args:
        tags (list): A list of tags to search for within the metadata.
        metadata_list (list): A list of dictionaries containing image metadata.

    Returns:
        tuple|bool: A tuple containing a list of matching image IDs and the count of matches,
                    or False if no matches are found.

    Raises:
        Exception: If an error occurs during the search process, it will be printed to the console.
    """
    try:
        search_results = []
        count = 0
        for image_entry in metadata_list:
            for tag in tags:
                if tag in image_entry["tags"]:
                    if image_entry["id"] not in search_results:
                        search_results.append(image_entry["id"])
                        count += 1
        if count != 0:
            return search_results, count
        else:
            print("No images found that match the search tags.")
            return search_results
    except Exception as err:
        print("Error encountered during searching through tags: ", err)
        return False


def print_matching_data(meta_data, search_results):
    """
    Prints the metadata of images that match the provided search results.

    Args:
        meta_data (list): A list of dictionaries containing image metadata.
        search_results (list): A list of image IDs that match the search criteria.

    Returns:
        None
    """
    matching_data = [data for data in meta_data if data["id"] in search_results]
    for data in matching_data:
        print(json.dumps(data, indent=4))


def main():
    """
    The main function that drives the script. It loads metadata from a JSON file,
    prompts the user for search keywords, and then performs searches based on those
    keywords using both tags and labels. The matching results are printed to the console.

    Returns:
        None

    Raises:
        Exception: If an error occurs during file handling or any other operations,
                   it will be printed to the console.
    """
    try:
        with open("meta_data.json", "r") as json_file:
            meta_data = json.load(json_file)
        keywords = input("Enter a comma-separated list of keywords: ").split(",")
        tags_results = search_tags(keywords, meta_data)
        search_results = search_labels(
            keywords, meta_data, tags_results, count=len(tags_results)
        )
        counter = 1
        for key in search_results:
            print(counter, ") Search result: ", key)
            counter += 1
        print_matching_data(meta_data, search_results)
    except Exception as err:
        print("Error encountered: ", err)


if __name__ == "__main__":
    main()
