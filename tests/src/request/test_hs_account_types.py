import pytest

from src.request.common import HSAccountTypes


def tests_are_unique():
    names = [e.name for e in HSAccountTypes]
    assert len(names) == len(set(names))


@pytest.mark.parametrize(
    "account_type, expected_value",
    [
        (HSAccountTypes.regular, "hiscore_oldschool"),
        (HSAccountTypes.pure, "hiscore_oldschool_skiller_defence"),
        (HSAccountTypes.im, "hiscore_oldschool_ironman"),
        (HSAccountTypes.uim, "hiscore_oldschool_ultimate"),
        (HSAccountTypes.hc, "hiscore_oldschool_hardcore_ironman"),
        (HSAccountTypes.skiller, "hiscore_oldschool_skiller"),
    ],
)
def test_values(account_type: HSAccountTypes, expected_value: str):
    assert account_type.value == expected_value


@pytest.mark.parametrize(
    "account_type, expected_path",
    [
        (HSAccountTypes.regular, "hiscore_oldschool"),
        (HSAccountTypes.pure, "hiscore_oldschool_skiller_defence"),
        (HSAccountTypes.im, "hiscore_oldschool_ironman"),
        (HSAccountTypes.uim, "hiscore_oldschool_ultimate"),
        (HSAccountTypes.hc, "hiscore_oldschool_hardcore_ironman"),
        (HSAccountTypes.skiller, "hiscore_oldschool_skiller"),
    ],
)
def test_lookup_overall(account_type: HSAccountTypes, expected_path: str):
    assert account_type.lookup_overall(
    ) == f"https://secure.runescape.com/m={expected_path}/overall"


@pytest.mark.parametrize(
    "account_type, expected_path",
    [
        (HSAccountTypes.regular, "hiscore_oldschool"),
        (HSAccountTypes.pure, "hiscore_oldschool_skiller_defence"),
        (HSAccountTypes.im, "hiscore_oldschool_ironman"),
        (HSAccountTypes.uim, "hiscore_oldschool_ultimate"),
        (HSAccountTypes.hc, "hiscore_oldschool_hardcore_ironman"),
        (HSAccountTypes.skiller, "hiscore_oldschool_skiller"),
    ],
)
def test_lookup_personal(account_type: HSAccountTypes, expected_path: str):
    assert account_type.lookup_personal(
    ) == f"https://secure.runescape.com/m={expected_path}/hiscorepersonal"


@pytest.mark.parametrize(
    "account_type, expected_path",
    [
        (HSAccountTypes.regular, "hiscore_oldschool"),
        (HSAccountTypes.pure, "hiscore_oldschool_skiller_defence"),
        (HSAccountTypes.im, "hiscore_oldschool_ironman"),
        (HSAccountTypes.uim, "hiscore_oldschool_ultimate"),
        (HSAccountTypes.hc, "hiscore_oldschool_hardcore_ironman"),
        (HSAccountTypes.skiller, "hiscore_oldschool_skiller"),
    ],
)
def test_api_csv(account_type: HSAccountTypes, expected_path: str):
    assert account_type.api_csv(
    ) == f"https://secure.runescape.com/m={expected_path}/index_lite.ws"


@pytest.mark.parametrize(
    "account_type, expected_path",
    [
        (HSAccountTypes.regular, "hiscore_oldschool"),
        (HSAccountTypes.pure, "hiscore_oldschool_skiller_defence"),
        (HSAccountTypes.im, "hiscore_oldschool_ironman"),
        (HSAccountTypes.uim, "hiscore_oldschool_ultimate"),
        (HSAccountTypes.hc, "hiscore_oldschool_hardcore_ironman"),
        (HSAccountTypes.skiller, "hiscore_oldschool_skiller"),
    ],
)
def test_api_json(account_type: HSAccountTypes, expected_path: str):
    assert account_type.api_json(
    ) == f"https://secure.runescape.com/m={expected_path}/index_lite.json"


@pytest.mark.parametrize(
    "account_type, expected_value",
    [
        ("regular", HSAccountTypes.regular),
        ("pure", HSAccountTypes.pure),
        ("im", HSAccountTypes.im),
        ("uim", HSAccountTypes.uim),
        ("hc", HSAccountTypes.hc),
        ("skiller", HSAccountTypes.skiller),
    ],
)
def test_from_string_parse(account_type: str, expected_value: HSAccountTypes):
    assert HSAccountTypes.from_string(account_type) == expected_value


@pytest.mark.parametrize(
    "account_type",
    [
        ("reular"),
        ("pue"),
        ("test"),
    ],
)
def test_from_string_keyerror(account_type: str):
    with pytest.raises(KeyError):
        HSAccountTypes.from_string(account_type)
