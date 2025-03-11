import json

def save_json(filepath: str, data):
    """
    Saves the given data as JSON to the specified filepath.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_json(filepath: str):
    """
    Loads JSON data from the specified filepath.
    Returns the data if successful, or None if file not found or invalid.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def convert_lists_to_sets(obj):
    """
    Recursively converts lists within the object to sets.
    Use with caution as this may affect ordering.
    """
    if isinstance(obj, dict):
        return {k: convert_lists_to_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return {convert_lists_to_sets(i) for i in obj}
    return obj
