import pytest
from src.util.predicate_utils import get_comparison

PREDICATES = {
        "<": lambda a: a < 10,
        "<=": lambda a: a <= 10,
        ">": lambda a: a > 10,
        ">=": lambda a: a >= 10,
        "==": lambda a: a == 10,
        "!=": lambda a: a != 10,
    }

class ValidWrapper:
    def __init__(self, pred):
        self.p = pred
        self.pred = pred
        self.predicate = pred

class InValidWrapper:
    def __init__(self, pred):
        self.random_name = pred


def test_get_comparison_valid_simple():
    for sign, predicate in PREDICATES.items():
        res = get_comparison(predicate)
        assert res == sign

def test_get_comparison_valid_wrapped_class():
    for sign, predicate in PREDICATES.items():
        res = get_comparison(ValidWrapper(pred=predicate).pred)
        assert res == sign


def test_get_comparison_valid_wrapped_function():
    for sign, predicate in PREDICATES.items():
        pred = lambda values: any(predicate(v) for v in values)
        res = get_comparison(pred)
        assert res == sign

def test_get_comparison_valid_wrapped_class_and_function():
    for sign, predicate in PREDICATES.items():
        wrapper = ValidWrapper(pred=predicate)

        pred = lambda values: any(wrapper.p(v) for v in values)
        res = get_comparison(pred)
        assert res == sign

        pred = lambda values: any(wrapper.pred(v) for v in values)
        res = get_comparison(pred)
        assert res == sign

        pred = lambda values: any(wrapper.predicate(v) for v in values)
        res = get_comparison(pred)
        assert res == sign

def test_get_comparison_invalid_wrapped_class_and_function():
    for _, predicate in PREDICATES.items():
        wrapper = InValidWrapper(pred=predicate)
        pred = lambda values: any(wrapper.random_name(v) for v in values)
        with pytest.raises(ValueError):
            _ = get_comparison(pred)