import pytest

from osrs_hiscore_scrape.request.hs_types import HSIncrementer, HSType, HSValue


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


def test_hs_type_is_skill():
    test_cases = {
        HSType.overall,
        HSType.attack,
        HSType.defence,
        HSType.strength,
        HSType.hitpoints,
        HSType.ranged,
        HSType.prayer,
        HSType.magic,
        HSType.cooking,
        HSType.woodcutting,
        HSType.fletching,
        HSType.fishing,
        HSType.firemaking,
        HSType.crafting,
        HSType.smithing,
        HSType.mining,
        HSType.herblore,
        HSType.agility,
        HSType.thieving,
        HSType.slayer,
        HSType.farming,
        HSType.runecrafting,
        HSType.hunter,
        HSType.construction,
        HSType.sailing,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_skill() for hs in test_cases)
    assert all(not hs.is_skill() for hs in delta)


def test_hs_type_is_activity():
    test_cases = {
        HSType.grid_points,
        HSType.league_points,
        HSType.dmm,
        HSType.bh_hunter,
        HSType.bh_rogue,
        HSType.bh_legacy_hunter,
        HSType.bh_legacy_rogue,
        HSType.clue_all,
        HSType.clue_beginner,
        HSType.clue_easy,
        HSType.clue_medium,
        HSType.clue_hard,
        HSType.clue_elite,
        HSType.clue_master,
        HSType.lms_rank,
        HSType.pvp_arena_rank,
        HSType.sw_zeal,
        HSType.rifts_closed,
        HSType.colosseum_glory,
        HSType.collections_logged,
        HSType.sire,
        HSType.hydra,
        HSType.amoxliatl,
        HSType.araxxor,
        HSType.artio,
        HSType.barrows_chests,
        HSType.brutus,
        HSType.bryophyta,
        HSType.callisto,
        HSType.calvarion,
        HSType.cerberus,
        HSType.cox,
        HSType.cox_cm,
        HSType.chaos_elemental,
        HSType.chaos_fanatic,
        HSType.saradomin,
        HSType.corp,
        HSType.crazy_archaeologist,
        HSType.dks_prime,
        HSType.dks_rex,
        HSType.dks_supreme,
        HSType.deranged_archaeologist,
        HSType.doom_mokhaiotl,
        HSType.duke,
        HSType.bandos,
        HSType.giant_mole,
        HSType.gg,
        HSType.hespori,
        HSType.kq,
        HSType.kbd,
        HSType.kraken,
        HSType.armadyl,
        HSType.zamorak,
        HSType.lunar_chests,
        HSType.mimic,
        HSType.nex,
        HSType.nightmare,
        HSType.psn,
        HSType.obor,
        HSType.phantom_muspah,
        HSType.sarachnis,
        HSType.scorpia,
        HSType.scurrius,
        HSType.shellbane_gryphon,
        HSType.skotizo,
        HSType.sol,
        HSType.spindel,
        HSType.tempoross,
        HSType.gauntlet,
        HSType.cg,
        HSType.hueycoatl,
        HSType.leviathan,
        HSType.royal_titans,
        HSType.whisperer,
        HSType.tob,
        HSType.hmt,
        HSType.thermy,
        HSType.toa,
        HSType.toa_em,
        HSType.zuk,
        HSType.jad,
        HSType.vardorvis,
        HSType.venenatis,
        HSType.vetion,
        HSType.vorkath,
        HSType.wt,
        HSType.yama,
        HSType.zalcano,
        HSType.zulrah,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_activity() for hs in test_cases)
    assert all(not hs.is_activity() for hs in delta)

def test_hs_type_is_seasonal_mode():
    test_cases = {
        HSType.grid_points,
        HSType.league_points,
        HSType.dmm,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_seasonal_mode() for hs in test_cases)
    assert all(not hs.is_seasonal_mode() for hs in delta)


def test_hs_type_is_clue():
    test_cases = {
        HSType.clue_all,
        HSType.clue_beginner,
        HSType.clue_easy,
        HSType.clue_medium,
        HSType.clue_hard,
        HSType.clue_elite,
        HSType.clue_master,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_clue() for hs in test_cases)
    assert all(not hs.is_clue() for hs in delta)


def test_hs_type_is_minigame():
    test_cases = {
        HSType.bh_hunter,
        HSType.bh_rogue,
        HSType.bh_legacy_hunter,
        HSType.bh_legacy_rogue,
        HSType.lms_rank,
        HSType.pvp_arena_rank,
        HSType.sw_zeal,
        HSType.rifts_closed,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_minigame() for hs in test_cases)
    assert all(not hs.is_minigame() for hs in delta)


def test_hs_type_is_misc():
    test_cases = {
        HSType.colosseum_glory,
        HSType.collections_logged,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_misc() for hs in test_cases)
    assert all(not hs.is_misc() for hs in delta)


def test_hs_type_is_boss():
    test_cases = {
        HSType.sire,
        HSType.hydra,
        HSType.amoxliatl,
        HSType.araxxor,
        HSType.artio,
        HSType.barrows_chests,
        HSType.brutus,
        HSType.bryophyta,
        HSType.callisto,
        HSType.calvarion,
        HSType.cerberus,
        HSType.cox,
        HSType.cox_cm,
        HSType.chaos_elemental,
        HSType.chaos_fanatic,
        HSType.saradomin,
        HSType.corp,
        HSType.crazy_archaeologist,
        HSType.dks_prime,
        HSType.dks_rex,
        HSType.dks_supreme,
        HSType.deranged_archaeologist,
        HSType.doom_mokhaiotl,
        HSType.duke,
        HSType.bandos,
        HSType.giant_mole,
        HSType.gg,
        HSType.hespori,
        HSType.kq,
        HSType.kbd,
        HSType.kraken,
        HSType.armadyl,
        HSType.zamorak,
        HSType.lunar_chests,
        HSType.mimic,
        HSType.nex,
        HSType.nightmare,
        HSType.psn,
        HSType.obor,
        HSType.phantom_muspah,
        HSType.sarachnis,
        HSType.scorpia,
        HSType.scurrius,
        HSType.shellbane_gryphon,
        HSType.skotizo,
        HSType.sol,
        HSType.spindel,
        HSType.tempoross,
        HSType.gauntlet,
        HSType.cg,
        HSType.hueycoatl,
        HSType.leviathan,
        HSType.royal_titans,
        HSType.whisperer,
        HSType.tob,
        HSType.hmt,
        HSType.thermy,
        HSType.toa,
        HSType.toa_em,
        HSType.zuk,
        HSType.jad,
        HSType.vardorvis,
        HSType.venenatis,
        HSType.vetion,
        HSType.vorkath,
        HSType.wt,
        HSType.yama,
        HSType.zalcano,
        HSType.zulrah,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_boss() for hs in test_cases)
    assert all(not hs.is_boss() for hs in delta)


def test_hs_type_is_combat():
    test_cases = {
        HSType.attack, 
        HSType.defence, 
        HSType.strength, 
        HSType.hitpoints,
        HSType.ranged, 
        HSType.prayer, 
        HSType.magic, 
        HSType.combat
    }
    delta = set(HSType) - test_cases

    assert all(hs.is_combat() for hs in test_cases)
    assert all(not hs.is_combat() for hs in delta)


def test_hs_type_combat_special_case():
    combat = HSType.combat
    assert combat.get_category() == -1
    assert combat.get_category_value() == -1
    assert combat.get_csv_value() == -1


def test_hs_type_csv_len():
    assert HSType.csv_len() == 114  # run api to see count


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
