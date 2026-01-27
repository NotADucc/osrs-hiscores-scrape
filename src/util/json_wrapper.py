import json
from typing import Any
from dataclasses import asdict

_json_lib = json

class PlayerRecordEncoder(json.JSONEncoder):
    def default(self, obj): # type: ignore
        from src.request.results import PlayerRecordInfo
        if isinstance(obj, PlayerRecordInfo):
            return asdict(obj) # type: ignore
        return super().default(obj)


def to_json(data: Any, **kwargs) -> str:
    """ Serialize an object to a JSON-formatted string. """
    return _json_lib.dumps(data, **kwargs, cls=PlayerRecordEncoder)


def from_json(json_string: str, **kwargs) -> Any:
    """ Deserialize a JSON-formatted string into an object. """
    return _json_lib.loads(json_string, **kwargs)
