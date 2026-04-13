import json

def json_to_dict(json_string: str) -> dict:
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return None

def dict_to_json(data_dict: dict, indent=4) -> str:
    try:
        json_string = json.dumps(data_dict, indent=indent)
        return json_string
    except (TypeError, ValueError) as e:
        print("Cannot convert dictionary to JSON:", e)
        return None