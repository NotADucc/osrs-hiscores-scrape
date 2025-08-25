import json
from typing import Any

_json_lib = json


def to_json(data: Any, **kwargs) -> str:
    """ Serialize an object to a JSON-formatted string. """
    return _json_lib.dumps(data, **kwargs)


def from_json(json_string: str, **kwargs) -> Any:
    """ Deserialize a JSON-formatted string into an object. """
    return _json_lib.loads(json_string, **kwargs)
