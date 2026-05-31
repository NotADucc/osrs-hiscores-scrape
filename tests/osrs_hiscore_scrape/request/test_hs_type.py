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


def test_hs_incrementer_skill():
    incr = HSIncrementer()

    val = incr.skill()

    assert val.category == 0
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.skill()

    assert val.category == 0
    assert val.category_value == 1
    assert val.csv_value == 1


def test_hs_incrementer_activity():
    incr = HSIncrementer()

    val = incr.activity()

    assert val.category == 1
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.activity()

    assert val.category == 1
    assert val.category_value == 1
    assert val.csv_value == 1


def test_hs_incrementer_activity_false():
    incr = HSIncrementer()

    val = incr.activity(False)

    assert val.category == 1
    assert val.category_value == 0
    assert val.csv_value == -1

    val = incr.activity()

    assert val.category == 1
    assert val.category_value == 1
    assert val.csv_value == 0


def test_hs_incrementer_mix():
    incr = HSIncrementer()

    val = incr.skill()

    assert val.category == 0
    assert val.category_value == 0
    assert val.csv_value == 0

    val = incr.activity()

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
        HSType.deadman_points,
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
        HSType.soulwars_zeal,
        HSType.rifts_closed,
        HSType.colosseum_glory,
        HSType.collections_logged,
        HSType.abyssal_sire,
        HSType.alchemical_hydra,
        HSType.amoxliatl,
        HSType.araxxor,
        HSType.artio,
        HSType.barrows_chests,
        HSType.brutus,
        HSType.bryophyta,
        HSType.callisto,
        HSType.calvarion,
        HSType.cerberus,
        HSType.chambers_of_xeric,
        HSType.chambers_of_xeric_challenge_mode,
        HSType.chaos_elemental,
        HSType.chaos_fanatic,
        HSType.commander_zilyana,
        HSType.corporeal_beast,
        HSType.crazy_archaeologist,
        HSType.dagannoth_prime,
        HSType.dagannoth_rex,
        HSType.dagannoth_supreme,
        HSType.deranged_archaeologist,
        HSType.doom_of_mokhaiotl,
        HSType.duke_sucellus,
        HSType.general_graardor,
        HSType.giant_mole,
        HSType.grotesque_guardians,
        HSType.hespori,
        HSType.kalphite_queen,
        HSType.king_black_dragon,
        HSType.kraken,
        HSType.kree_arra,
        HSType.kril_tsutsaroth,
        HSType.lunar_chests,
        HSType.mimic,
        HSType.nex,
        HSType.nightmare,
        HSType.phosanis_nightmare,
        HSType.obor,
        HSType.phantom_muspah,
        HSType.sarachnis,
        HSType.scorpia,
        HSType.scurrius,
        HSType.shellbane_gryphon,
        HSType.skotizo,
        HSType.sol_heredit,
        HSType.spindel,
        HSType.tempoross,
        HSType.the_gauntlet,
        HSType.the_corrupted_gauntlet,
        HSType.the_hueycoatl,
        HSType.the_leviathan,
        HSType.the_royal_titans,
        HSType.the_whisperer,
        HSType.theatre_of_blood,
        HSType.theatre_of_blood_hard_mode,
        HSType.thermonuclear_smoke_devil,
        HSType.tombs_of_amascut,
        HSType.tombs_of_amascut_expert_mode,
        HSType.tzkal_zuk,
        HSType.tztok_jad,
        HSType.vardorvis,
        HSType.venenatis,
        HSType.vetion,
        HSType.vorkath,
        HSType.wintertodt,
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
        HSType.cs_all,
        HSType.clue_beginner,
        HSType.cs_beginner,
        HSType.clue_easy,
        HSType.cs_easy,
        HSType.clue_medium,
        HSType.cs_medium,
        HSType.clue_hard,
        HSType.cs_hard,
        HSType.clue_elite,
        HSType.cs_elite,
        HSType.clue_master,
        HSType.cs_master,
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
        HSType.soulwars_zeal,
        HSType.rifts_closed,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_minigame() for hs in test_cases)
    assert all(not hs.is_minigame() for hs in delta)


def test_hs_type_is_misc():
    test_cases = {
        HSType.colosseum_glory,
        HSType.glory,
        HSType.collections_logged,
        HSType.clog,
    }
    delta = set(HSType) - test_cases - {HSType.combat}

    assert all(hs.is_misc() for hs in test_cases)
    assert all(not hs.is_misc() for hs in delta)


def test_hs_type_is_boss():
    test_cases = {
        HSType.abyssal_sire,
        HSType.alchemical_hydra,
        HSType.amoxliatl,
        HSType.araxxor,
        HSType.artio,
        HSType.barrows_chests,
        HSType.brutus,
        HSType.bryophyta,
        HSType.callisto,
        HSType.calvarion,
        HSType.cerberus,
        HSType.chambers_of_xeric,
        HSType.chambers_of_xeric_challenge_mode,
        HSType.chaos_elemental,
        HSType.chaos_fanatic,
        HSType.commander_zilyana,
        HSType.corporeal_beast,
        HSType.crazy_archaeologist,
        HSType.dagannoth_prime,
        HSType.dagannoth_rex,
        HSType.dagannoth_supreme,
        HSType.deranged_archaeologist,
        HSType.doom_of_mokhaiotl,
        HSType.duke_sucellus,
        HSType.general_graardor,
        HSType.giant_mole,
        HSType.grotesque_guardians,
        HSType.hespori,
        HSType.kalphite_queen,
        HSType.king_black_dragon,
        HSType.kraken,
        HSType.kree_arra,
        HSType.kril_tsutsaroth,
        HSType.lunar_chests,
        HSType.mimic,
        HSType.nex,
        HSType.nightmare,
        HSType.phosanis_nightmare,
        HSType.obor,
        HSType.phantom_muspah,
        HSType.sarachnis,
        HSType.scorpia,
        HSType.scurrius,
        HSType.shellbane_gryphon,
        HSType.skotizo,
        HSType.sol_heredit,
        HSType.spindel,
        HSType.tempoross,
        HSType.the_gauntlet,
        HSType.the_corrupted_gauntlet,
        HSType.the_hueycoatl,
        HSType.the_leviathan,
        HSType.the_royal_titans,
        HSType.the_whisperer,
        HSType.theatre_of_blood,
        HSType.theatre_of_blood_hard_mode,
        HSType.thermonuclear_smoke_devil,
        HSType.tombs_of_amascut,
        HSType.tombs_of_amascut_expert_mode,
        HSType.tzkal_zuk,
        HSType.tztok_jad,
        HSType.vardorvis,
        HSType.venenatis,
        HSType.vetion,
        HSType.vorkath,
        HSType.wintertodt,
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
        HSType.att,
        HSType.defence,
        HSType.defe,
        HSType.strength,
        HSType.stre,
        HSType.hitpoints,
        HSType.hp,
        HSType.ranged,
        HSType.range,
        HSType.prayer,
        HSType.pray,
        HSType.magic,
        HSType.mage,
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
        ("str"),  # reserved typing
        ("def"),  # reserved keyword
        ("atta"),
        ("test"),
    ],
)
def test_hs_type_from_string_key_error(account_type: str):
    with pytest.raises(ValueError):
        HSType.from_string(account_type)


def test_hs_type_skill_shorthand_names():
    assert HSType.attack == HSType.att == HSType.atk
    assert HSType.defence == HSType.defe
    assert HSType.strength == HSType.stre
    assert HSType.hitpoints == HSType.hp
    assert HSType.ranged == HSType.range
    assert HSType.prayer == HSType.pray
    assert HSType.magic == HSType.mage
    assert HSType.cooking == HSType.cook
    assert HSType.woodcutting == HSType.wc
    assert HSType.fletching == HSType.fletch
    assert HSType.fishing == HSType.fish
    assert HSType.firemaking == HSType.fm == HSType.fire
    assert HSType.crafting == HSType.craft
    assert HSType.smithing == HSType.smith
    assert HSType.mining == HSType.mine
    assert HSType.herblore == HSType.herb
    assert HSType.agility == HSType.agil
    assert HSType.thieving == HSType.thiev
    assert HSType.slayer == HSType.slay
    assert HSType.farming == HSType.farm
    assert HSType.runecrafting == HSType.rc == HSType.rune
    assert HSType.hunter == HSType.hunt
    assert HSType.construction == HSType.con
    assert HSType.sailing == HSType.sail


def test_hs_type_seasonal_shorthand_names():
    assert HSType.league_points == HSType.leagues
    assert HSType.deadman_points == HSType.dmm


def test_hs_type_minigames_shorthand_names():
    assert HSType.bh_legacy_hunter == HSType.bhl_hunter
    assert HSType.bh_legacy_rogue == HSType.bhl_rogue
    assert HSType.soulwars_zeal == HSType.sw_zeal


def test_hs_type_clues_shorthand_names():
    assert HSType.clue_all == HSType.cs_all
    assert HSType.clue_beginner == HSType.cs_beginner
    assert HSType.clue_easy == HSType.cs_easy
    assert HSType.clue_medium == HSType.cs_medium
    assert HSType.clue_hard == HSType.cs_hard
    assert HSType.clue_elite == HSType.cs_elite
    assert HSType.clue_master == HSType.cs_master


def test_hs_type_misc_shorthand_names():
    assert HSType.colosseum_glory == HSType.glory
    assert HSType.collections_logged == HSType.clog


def test_hs_type_boss_shorthand_names():
    assert HSType.abyssal_sire == HSType.sire
    assert HSType.alchemical_hydra == HSType.hydra
    assert HSType.amoxliatl == HSType.amox
    assert HSType.barrows_chests == HSType.barrows
    assert HSType.bryophyta == HSType.bryo
    assert HSType.cerberus == HSType.cerb
    assert HSType.chambers_of_xeric == HSType.cox
    assert HSType.chambers_of_xeric_challenge_mode == HSType.cox_cm == HSType.raids1
    assert HSType.chaos_elemental == HSType.chaos_ele
    assert HSType.chaos_fanatic == HSType.chaos_fan
    assert HSType.commander_zilyana == HSType.zily == HSType.sara == HSType.saradomin
    assert HSType.corporeal_beast == HSType.corp
    assert HSType.crazy_archaeologist == HSType.crazy_arch
    assert HSType.dagannoth_prime == HSType.prime
    assert HSType.dagannoth_rex == HSType.rex
    assert HSType.dagannoth_supreme == HSType.supreme
    assert HSType.deranged_archaeologist == HSType.deranged_arch
    assert HSType.doom_of_mokhaiotl == HSType.doom
    assert HSType.duke_sucellus == HSType.duke
    assert HSType.general_graardor == HSType.graardor == HSType.bandos
    assert HSType.giant_mole == HSType.mole
    assert HSType.grotesque_guardians == HSType.ggs == HSType.dusk
    assert HSType.kalphite_queen == HSType.kq
    assert HSType.king_black_dragon == HSType.kbd
    assert HSType.kree_arra == HSType.kree == HSType.arma == HSType.armadyl
    assert HSType.kril_tsutsaroth == HSType.kril == HSType.zammy == HSType.zamorak
    assert HSType.lunar_chests == HSType.moons
    assert HSType.nightmare == HSType.nm
    assert HSType.phosanis_nightmare == HSType.psn == HSType.phosani
    assert HSType.phantom_muspah == HSType.muspah == HSType.grumbler == HSType.pm
    assert HSType.shellbane_gryphon == HSType.gryphon
    assert HSType.sol_heredit == HSType.sol
    assert HSType.tempoross == HSType.fishtodt
    assert HSType.the_gauntlet == HSType.gauntlet == HSType.gaunt
    assert HSType.the_corrupted_gauntlet == HSType.cg
    assert HSType.the_hueycoatl == HSType.hueycoatl == HSType.huey
    assert HSType.the_leviathan == HSType.leviathan == HSType.levi
    assert HSType.the_royal_titans == HSType.royal_titans == HSType.titans
    assert HSType.the_whisperer == HSType.whisperer == HSType.whisp
    assert HSType.theatre_of_blood == HSType.tob == HSType.raids2
    assert HSType.theatre_of_blood_hard_mode == HSType.hmt
    assert HSType.thermonuclear_smoke_devil == HSType.thermy
    assert HSType.tombs_of_amascut == HSType.toa == HSType.raids3
    assert HSType.tombs_of_amascut_expert_mode == HSType.toa_expert
    assert HSType.tzkal_zuk == HSType.zuk == HSType.inferno
    assert HSType.tztok_jad == HSType.jad == HSType.fc
    assert HSType.vardorvis == HSType.vard
    assert HSType.venenatis == HSType.vene
    assert HSType.vorkath == HSType.vork
    assert HSType.wintertodt == HSType.wt
    assert HSType.zalcano == HSType.zalc


def test_hiscore_enum_ordering():
    expected = [
        "overall",
        "attack",
        "defence",
        "strength",
        "hitpoints",
        "ranged",
        "prayer",
        "magic",
        "cooking",
        "woodcutting",
        "fletching",
        "fishing",
        "firemaking",
        "crafting",
        "smithing",
        "mining",
        "herblore",
        "agility",
        "thieving",
        "slayer",
        "farming",
        "runecrafting",
        "hunter",
        "construction",
        "sailing",
        "grid_points",
        "league_points",
        "deadman_points",
        "bh_hunter",
        "bh_rogue",
        "bh_legacy_hunter",
        "bh_legacy_rogue",
        "clue_all",
        "clue_beginner",
        "clue_easy",
        "clue_medium",
        "clue_hard",
        "clue_elite",
        "clue_master",
        "lms_rank",
        "pvp_arena_rank",
        "soulwars_zeal",
        "rifts_closed",
        "colosseum_glory",
        "collections_logged",
        "abyssal_sire",
        "alchemical_hydra",
        "amoxliatl",
        "araxxor",
        "artio",
        "barrows_chests",
        "brutus",
        "bryophyta",
        "callisto",
        "calvarion",
        "cerberus",
        "chambers_of_xeric",
        "chambers_of_xeric_challenge_mode",
        "chaos_elemental",
        "chaos_fanatic",
        "commander_zilyana",
        "corporeal_beast",
        "crazy_archaeologist",
        "dagannoth_prime",
        "dagannoth_rex",
        "dagannoth_supreme",
        "deranged_archaeologist",
        "doom_of_mokhaiotl",
        "duke_sucellus",
        "general_graardor",
        "giant_mole",
        "grotesque_guardians",
        "hespori",
        "kalphite_queen",
        "king_black_dragon",
        "kraken",
        "kree_arra",
        "kril_tsutsaroth",
        "lunar_chests",
        "mimic",
        "nex",
        "nightmare",
        "phosanis_nightmare",
        "obor",
        "phantom_muspah",
        "sarachnis",
        "scorpia",
        "scurrius",
        "shellbane_gryphon",
        "skotizo",
        "sol_heredit",
        "spindel",
        "tempoross",
        "the_gauntlet",
        "the_corrupted_gauntlet",
        "the_hueycoatl",
        "the_leviathan",
        "the_royal_titans",
        "the_whisperer",
        "theatre_of_blood",
        "theatre_of_blood_hard_mode",
        "thermonuclear_smoke_devil",
        "tombs_of_amascut",
        "tombs_of_amascut_expert_mode",
        "tzkal_zuk",
        "tztok_jad",
        "vardorvis",
        "venenatis",
        "vetion",
        "vorkath",
        "wintertodt",
        "yama",
        "zalcano",
        "zulrah",
    ]

    actual = [member.name for member in HSType]
    actual.pop(-1) # remove combat

    assert actual == expected