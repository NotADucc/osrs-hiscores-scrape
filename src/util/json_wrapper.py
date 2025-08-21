import json
from typing import Any

_json_lib = json


def to_json(data: Any, **kwargs) -> str:
    """
    Serialize an object to a JSON-formatted string.

    Args:
        data (Any): The object to serialize.
        **kwargs: Additional keyword arguments passed to `json.dumps`.

    Returns:
        str: The JSON-formatted string representation of `data`.
    """

    return _json_lib.dumps(data, **kwargs)


def from_json(json_string: str, **kwargs) -> Any:
    """
    Deserialize a JSON-formatted string into an object.

    Args:
        json_string (str): The JSON string to deserialize.
        **kwargs: Additional keyword arguments passed to `json.loads`.

    Returns:
        Any: The resulting object.
    """

    return _json_lib.loads(json_string, **kwargs)
