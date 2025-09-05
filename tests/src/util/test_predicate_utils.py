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

class ValidWrapperWeirdName:
    def __init__(self, pred):
        self.weird_name = pred

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
        def pred(values): return any(predicate(v) for v in values)
        res = get_comparison(pred)
        assert res == sign


def test_get_comparison_valid_wrapped_class_and_function():
    for sign, predicate in PREDICATES.items():
        wrapper = ValidWrapper(pred=predicate)
        wrapper_weird_name = ValidWrapperWeirdName(pred=predicate)

        def pred1(values): return any(wrapper.p(v) for v in values)
        res = get_comparison(pred1)
        assert res == sign

        def pred2(values): return any(wrapper.pred(v) for v in values)
        res = get_comparison(pred2)
        assert res == sign

        def pred3(values): return any(wrapper.predicate(v) for v in values)
        res = get_comparison(pred3)
        assert res == sign

        def pred4(values): return any(wrapper_weird_name.weird_name(v) for v in values)
        res = get_comparison(pred4)
        assert res == sign