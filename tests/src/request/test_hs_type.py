import pytest

from src.request.common import HSIncrementer, HSType, HSValue


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
    hs_value = HSValue(category=category,
                       category_value=category_value, csv_value=csv_value)

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


def test_hs_incrementer_misc_false():
    incr = HSIncrementer()

    val = incr.misc_increment(False)

    assert val.category == 1
    assert val.category_value == 0
    assert val.csv_value == -1

    val = incr.misc_increment()

    assert val.category == 1
    assert val.category_value == 1
    assert val.csv_value == 0


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


def test_hs_type_csv_len():
    assert HSType.csv_len() == 112  # run api to see count


def test_hs_type_get_csv_types():
    lst = HSType.get_csv_types()
    assert len(lst) == HSType.csv_len()


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
