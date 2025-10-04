"""
Helper functions for JSON processing in the API.
"""

import json
import re
from typing import Any, Dict, Union


def clean_json_string(json_str: str) -> str:
    """
    Clean a potentially malformed JSON string by:
    1. Removing trailing commas in arrays and objects
    2. Handling simple syntax errors
    
    Args:
        json_str: The JSON string to clean
        
    Returns:
        A cleaned JSON string that should be parseable
    """
    # Remove trailing commas in arrays (e.g., [1, 2, 3, ] -> [1, 2, 3])
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Remove trailing commas in objects (e.g., {"a": 1, "b": 2, } -> {"a": 1, "b": 2})
    json_str = re.sub(r',\s*}', '}', json_str)
    
    return json_str


def safe_parse_json(json_str: str) -> Union[Dict[str, Any], None]:
    """
    Safely parse a JSON string with error handling and fixing common issues.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        The parsed JSON data as a dictionary/list, or None if parsing failed
    """
    try:
        # First try parsing as-is
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Try to fix common JSON format issues and parse again
            cleaned_json = clean_json_string(json_str)
            return json.loads(cleaned_json)
        except json.JSONDecodeError:
            # If all attempts fail, return None
            return None
