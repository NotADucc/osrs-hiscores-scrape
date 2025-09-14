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


def test_get_comparison_simple():
    for sign, predicate in PREDICATES.items():
        res = get_comparison(predicate)
        assert res == sign


def test_get_comparison_wrapped_class():
    for sign, predicate in PREDICATES.items():
        res = get_comparison(ValidWrapper(pred=predicate).pred)
        assert res == sign


def test_get_comparison_wrapped_function():
    for sign, predicate in PREDICATES.items():
        def pred(values): return any(predicate(v) for v in values)
        res = get_comparison(pred)
        assert res == sign


def test_get_comparison_wrapped_class_and_function():
    for sign, predicate in PREDICATES.items():
        wrapper = ValidWrapper(pred=predicate)

        def pred1(values): return any(wrapper.p(v) for v in values)
        res = get_comparison(pred1)
        assert res == sign

        def pred2(values): return any(wrapper.pred(v) for v in values)
        res = get_comparison(pred2)
        assert res == sign

        def pred3(values): return any(wrapper.predicate(v) for v in values)
        res = get_comparison(pred3)
        assert res == sign


def test_get_comparison_wrapped_class_and_function_unknown_name():
    for _, predicate in PREDICATES.items():
        wrapper = InValidWrapper(pred=predicate)
        def pred(values): return any(wrapper.random_name(v) for v in values)
        with pytest.raises(ValueError):
            _ = get_comparison(pred)
