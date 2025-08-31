import json

import pytest

from src.util.json_wrapper import from_json, to_json


def test_to_json_valid_basic_types():
    assert to_json(123) == "123"
    assert to_json("hello") == '"hello"'
    assert to_json(True) == "true"
    assert to_json(None) == "null"


def test_from_json_valid_basic_types():
    assert from_json("123") == 123
    assert from_json('"hello"') == "hello"
    assert from_json("true") is True
    assert from_json("null") is None


def test_round_trip_dict():
    data = {"a": 1, "b": [1, 2, 3], "c": {"nested": "yes"}}
    json_str = to_json(data)
    result = from_json(json_str)
    assert result == data


def test_round_trip_list():
    data = [1, 2, 3, {"a": "b"}]
    json_str = to_json(data)
    result = from_json(json_str)
    assert result == data


def test_to_json_with_kwargs():
    data = {"z": 1, "a": 2}
    json_str = to_json(data, sort_keys=True)
    assert json_str.startswith('{"a": 2')


def test_from_json_with_kwargs():
    json_str = '{"a": 1, "b": 2}'
    result = from_json(json_str, object_hook=lambda d: {
                       k.upper(): v for k, v in d.items()})
    assert result == {"A": 1, "B": 2}


def test_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        from_json("{bad json}")
