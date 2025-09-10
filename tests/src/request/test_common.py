import pytest
from src.request.common import HSAccountTypes, HSIncrementer, HSType, HSValue


def tests_hs_account_types_are_unique():
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
def test_hs_account_types_values(account_type: HSAccountTypes, expected_value: str):
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
def test_hs_account_types_lookup_overall(account_type: HSAccountTypes, expected_path: str):
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
def test_hs_account_types_lookup_personal(account_type: HSAccountTypes, expected_path: str):
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
def test_hs_account_types_api_csv(account_type: HSAccountTypes, expected_path: str):
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
def test_hs_account_types_api_json(account_type: HSAccountTypes, expected_path: str):
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
def test_hs_account_types_from_string_parse(account_type: str, expected_value: HSAccountTypes):
    assert HSAccountTypes.from_string(account_type) == expected_value


@pytest.mark.parametrize(
    "account_type",
    [
        ("reular"),
        ("pue"),
        ("test"),
    ],
)
def test_hs_account_types_from_string_keyerror(account_type: str):
    with pytest.raises(KeyError):
        HSAccountTypes.from_string(account_type)

@pytest.mark.parametrize(
    "category, category_value, csv_value",
    [
        (-1, -1, -1),
        (0, 0, 0),
        (10, 50, 20),
        (1_000_000, 1_000_000, 1_000_000),
    ],
)
def test_hs_value(category: int, category_value: int, csv_value: int):
    hs_value = HSValue(category=category, category_value=category_value, csv_value=csv_value)

    assert hs_value.category == category
    assert hs_value.category_value == category_value
    assert hs_value.csv_value == csv_value


def test_hs_incrementer_skills():
    incr = HSIncrementer()

    val = incr.skill_increment()

    assert val.category == 0
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.skill_increment()

    assert val.category == 0
    assert val.category_value == 1
    assert val.csv_value == 1

def test_hs_incrementer_misc():
    incr = HSIncrementer()

    val = incr.misc_increment()

    assert val.category == 1
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.misc_increment()

    assert val.category == 1
    assert val.category_value == 1
    assert val.csv_value == 1

def test_hs_incrementer_mix():
    incr = HSIncrementer()

    val = incr.skill_increment()

    assert val.category == 0
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.misc_increment()

    assert val.category == 1
    assert val.category_value == 0
    assert val.csv_value == 1

def test_hs_type_are_unique():
    names = [e.name for e in HSType]
    assert len(names) == len(set(names))

def test_hs_type_getters_return_expected_types():
    for hs in list(HSType):
        assert isinstance(hs.get_category(), int)
        assert isinstance(hs.get_category_value(), int)
        assert isinstance(hs.get_csv_value(), int)

@pytest.mark.parametrize(
    "hs_type", 
    [
        HSType.attack, HSType.defence, HSType.strength,
        HSType.hitpoints, HSType.ranged, HSType.prayer,
        HSType.magic, HSType.combat
    ]
)
def test_hs_type_is_combat_true(hs_type: HSType):
    assert hs_type.is_combat()

@pytest.mark.parametrize(
    "hs_type", 
    [
        HSType.overall, HSType.cooking, HSType.woodcutting, HSType.hydra
    ]
)
def test_hs_type_is_combat_false(hs_type: HSType):
    assert not hs_type.is_combat()


def test_hs_type_is_skill_and_is_misc():
    assert HSType.attack.is_skill()
    assert not HSType.attack.is_misc()

    assert HSType.league_points.is_misc()
    assert not HSType.league_points.is_skill()


def test_hs_type_combat_special_case():
    combat = HSType.combat
    assert combat.get_category() == -1
    assert combat.get_category_value() == -1
    assert combat.get_csv_value() == -1
    assert combat.is_combat()


@pytest.mark.parametrize(
    "hs_type, expected_value",
    [
        ("overall", HSType.overall),
        ("construction", HSType.construction),
        ("league_points", HSType.league_points),
        ("collections_logged", HSType.collections_logged),
        ("sire", HSType.sire),
        ("combat", HSType.combat),
    ],
)
def test_hs_type_from_string_parse(hs_type: str, expected_value: HSType):
    assert HSType.from_string(hs_type) == expected_value


@pytest.mark.parametrize(
    "account_type",
    [
        ("def"),
        ("att"),
        ("test"),
    ],
)
def test_hs_type_from_string_key_error(account_type: str):
    with pytest.raises(KeyError):
        HSType.from_string(account_type)