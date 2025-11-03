import math
from datetime import datetime

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.request.results import PlayerRecord


def test_initialization():
    csv = [
        "268860,2084,295930696",
        "266928,99,14242654",
        "280783,99,13456742",
        "43284,99,55677817",
        "70704,99,53199316",
        "94093,99,44703139",
        "235893,93,7303463",
        "79187,99,26705319",
        "661536,89,4910495",
        "484344,87,3985524",
        "487105,90,5346606",
        "337872,91,5909925",
        "459856,94,8236998",
        "569453,82,2560057",
        "351128,86,3675876",
        "556119,83,2737341",
        "394735,85,3418223",
        "295541,85,3370940",
        "307555,91,5917343",
        "73718,99,18261333",
        "571743,88,4458740",
        "308001,82,2474862",
        "441064,82,2545592",
        "456447,83,2832391",
        "-1,-1",
        "-1,-1",
        "-1,-1",
        "-1,-1",
        "-1,-1",
        "-1,-1",
        "-1,-1",
        "73593,791",
        "1063927,3",
        "724155,7",
        "415163,31",
        "16463,524",
        "16696,181",
        "72424,45",
        "49525,1357",
        "-1,-1",
        "-1,-1",
        "353441,117",
        "6294,46841",
        "50863,609",
        "239640,53",
        "72580,1065",
        "28872,119",
        "6737,2222",
        "135351,20",
        "881090,27",
        "367892,5",
        "-1,-1",
        "212805,20",
        "228961,222",
        "316018,9",
        "-1,-1",
        "187141,25",
        "236760,25",
        "194804,57",
        "156445,31",
        "298563,26",
        "359704,30",
        "554754,30",
        "353344,31",
        "206446,25",
        "11652,180",
        "83043,188",
        "274327,100",
        "268316,82",
        "147236,141",
        "426252,26",
        "220266,50",
        "535217,31",
        "293732,957",
        "118665,101",
        "145595,100",
        "300159,25",
        "41828,7",
        "172730,25",
        "95784,13",
        "39449,29",
        "386295,5",
        "75423,191",
        "321441,25",
        "170547,25",
        "299766,32",
        "46726,58",
        "16401,11",
        "135930,20",
        "154012,159",
        "108586,36",
        "181865,100",
        "82940,70",
        "10943,1012",
        "66611,267",
        "12990,643",
        "74056,41",
        "-1,-1",
        "69680,1028",
        "160739,35",
        "107248,42",
        "98354,1",
        "245164,5",
        "22833,1316",
        "42013,300",
        "-1,-1",
        "167300,555",
        "667681,168",
        "21059,498",
        "256874,25",
        "345072,161"
    ]

    player_record = PlayerRecord("TestUser", csv, datetime(2025, 11, 3))

    assert player_record.username == "TestUser"
    assert player_record.rank == 268860
    assert player_record.total_level == 2084
    assert player_record.total_xp == 295930696
    assert math.isclose(player_record.combat_lvl, 125.35)

    skills_true = [
        HSType.attack, HSType.defence, HSType.strength, HSType.hitpoints, HSType.ranged,
        HSType.prayer, HSType.magic, HSType.cooking, HSType.woodcutting, HSType.fletching,
        HSType.fishing, HSType.firemaking, HSType.crafting, HSType.smithing, HSType.mining,
        HSType.herblore, HSType.agility, HSType.thieving, HSType.slayer, HSType.farming,
        HSType.runecrafting, HSType.hunter, HSType.construction,
    ]
    assert all(skill.name in player_record.skills for skill in skills_true)

    skills_false = []
    assert all(skill.name not in player_record.skills for skill in skills_false)

    minigames_true = [
        HSType.lms_rank, HSType.rifts_closed, HSType.colosseum_glory, HSType.collections_logged
    ]
    assert all(mg.name in player_record.misc for mg in minigames_true)

    minigames_false = [
        HSType.grid_points, HSType.league_points, HSType.dmm, HSType.bh_hunter, HSType.bh_rogue,
        HSType.bh_legacy_hunter, HSType.bh_legacy_rogue, HSType.pvp_arena_rank, HSType.sw_zeal
    ]
    assert all(mg.name not in player_record.misc for mg in minigames_false)

    clues_true = [
        HSType.clue_all, HSType.clue_beginner, HSType.clue_easy, HSType.clue_medium, HSType.clue_hard,
        HSType.clue_elite, HSType.clue_master
    ]
    assert all(clue.name in player_record.misc for clue in clues_true)

    clues_false = []
    assert all(clue.name not in player_record.misc for clue in clues_false)

    bosses_true = [
        HSType.sire, HSType.hydra, HSType.amoxliatl, HSType.araxxor, HSType.artio,

        HSType.barrows_chests, HSType.bryophyta,

        HSType.calvarion, HSType.cerberus, HSType.cox, HSType.chaos_elemental, HSType.chaos_fanatic, HSType.saradomin,
        HSType.corp, HSType.crazy_archaeologist,

        HSType.dks_prime, HSType.dks_rex, HSType.dks_supreme, HSType.deranged_archaeologist, HSType.doom_mokhaiotl, HSType.duke,

        HSType.bandos, HSType.giant_mole, HSType.gg,

        HSType.hespori,

        HSType.kq, HSType.kbd, HSType.kraken, HSType.armadyl, HSType.zamorak,

        HSType.lunar_chests,

        HSType.mimic,

        HSType.nex, HSType.nightmare, HSType.psn, HSType.obor, HSType.phantom_muspah,

        HSType.sarachnis, HSType.scorpia, HSType.scurrius, HSType.skotizo, HSType.sol,
        HSType.spindel,

        HSType.tempoross, HSType.gauntlet, HSType.cg, HSType.hueycoatl,
        HSType.leviathan, HSType.royal_titans, HSType.whisperer, HSType.tob, HSType.thermy,
        HSType.toa, HSType.toa_em,

        HSType.zuk, HSType.jad,

        HSType.vardorvis, HSType.venenatis,
        HSType.vorkath, HSType.wt, HSType.yama, HSType.zalcano, HSType.zulrah
    ]
    assert all(boss.name in player_record.misc for boss in bosses_true)

    bosses_false = [
        HSType.callisto, HSType.cox_cm, HSType.hmt, HSType.vetion
    ]
    assert all(boss.name not in player_record.misc for boss in bosses_false)


def test_initialization_incomplete_csv():
    csv = [
        "268860,2084,295930696",
    ]
    player_record = PlayerRecord("TestUser", csv, datetime(2025, 11, 3))

    assert player_record.username == "TestUser"
    assert player_record.rank == 268860
    assert player_record.total_level == 2084
    assert player_record.total_xp == 295930696
    assert math.isclose(player_record.combat_lvl, 3)

    assert not player_record.skills
    assert not player_record.misc


def tes_get_stat_overall(sample_player_record: PlayerRecord):
    assert sample_player_record.get_stat(
        HSType.overall) == sample_player_record.total_level


def test_get_stat_combat(sample_player_record: PlayerRecord):
    assert sample_player_record.get_stat(
        HSType.combat) == sample_player_record.combat_lvl


def test_get_stat_skill(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types()[1:]:
        if hs_type.is_skill():
            skill_lvl = sample_player_record.skills[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == skill_lvl


def test_get_stat_misc_returns_default(sample_player_record_incomplete: PlayerRecord):
    some_misc = next(h for h in HSType if h.is_misc())
    assert sample_player_record_incomplete.get_stat(some_misc) in (
        0, sample_player_record_incomplete.misc.get(some_misc.name, 0))


def test_meets_and_lacks_requirements(sample_player_record: PlayerRecord):
    req = HSFilterEntry(HSType.attack, lambda v: v >= 50)
    assert sample_player_record.meets_requirements([req])
    assert not sample_player_record.lacks_requirements([req])

    req_fail = HSFilterEntry(HSType.attack, lambda v: v > 99)
    assert not sample_player_record.meets_requirements([req_fail])
    assert sample_player_record.lacks_requirements([req_fail])


def test_ordering(sample_player_record: PlayerRecord, sample_player_record_csv_list: list[str], sample_ts: datetime):
    better_total = PlayerRecord(
        "BetterTotal", sample_player_record_csv_list, sample_ts)
    better_total.total_level = sample_player_record.total_level + 1

    assert sample_player_record < better_total
    assert better_total > sample_player_record
    assert not (sample_player_record == better_total)


def test_eq_same_values(sample_player_record: PlayerRecord, sample_player_record_csv_list: list[str], sample_ts: datetime):
    copy = PlayerRecord("TestUser", sample_player_record_csv_list, sample_ts)
    copy.total_level = sample_player_record.total_level
    copy.total_xp = sample_player_record.total_xp
    copy.rank = sample_player_record.rank

    assert sample_player_record == copy


def test_to_and_from_dict(sample_player_record: PlayerRecord):
    d = sample_player_record.to_dict()
    restored = PlayerRecord.from_dict(d)

    assert restored.username == sample_player_record.username
    assert restored.total_level == sample_player_record.total_level
    assert restored.skills == sample_player_record.skills
    assert restored.misc == sample_player_record.misc


def test_str_returns_json(sample_player_record: PlayerRecord):
    s = str(sample_player_record)
    assert s.startswith("{")
    assert '"username":"TestUser"' in s
    for hs_type in HSType.get_csv_types()[1:]:
        assert hs_type.name in s
