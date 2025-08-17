import json
from typing import Any

_json_lib = json

def to_json(data: Any, **kwargs) -> str:
    return _json_lib.dumps(data, **kwargs)

def from_json(json_string: str, **kwargs) -> Any:
    return _json_lib.loads(json_string, **kwargs)