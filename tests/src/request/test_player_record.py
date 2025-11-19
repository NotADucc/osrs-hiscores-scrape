import math
from datetime import datetime

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.request.results import PlayerRecord


def test_initialization():
    csv = [
        "271397,2084,297498066",
        "268217,99,14245636",
        "281065,99,13468883",
        "42648,99,56602511",
        "70450,99,53575268",
        "94472,99,44822933",
        "237673,93,7303472",
        "79477,99,26806626",
        "664934,89,4910495",
        "490358,87,3985524",
        "490144,90,5346606",
        "340319,91,5909925",
        "463083,94,8236998",
        "573517,82,2560057",
        "355281,86,3675876",
        "561031,83,2737341",
        "397626,85,3418223",
        "297883,85,3371009",
        "310011,91,5917957",
        "74375,99,18261333",
        "575387,88,4469496",
        "308677,82,2493914",
        "444326,82,2545592",
        "461147,83,2832391",
        "-1,1,1",
        "-1,0",
        "-1,0",
        "-1,0",
        "-1,0",
        "-1,0",
        "-1,0",
        "-1,0",
        "74395,791",
        "1069992,3",
        "727558,7",
        "417328,31",
        "16692,524",
        "16935,181",
        "72937,45",
        "49431,1357",
        "-1,1787",
        "-1,0",
        "357748,117",
        "6369,46841",
        "51787,609",
        "241728,53",
        "72994,1065",
        "29528,119",
        "6958,2222",
        "136540,20",
        "885064,27",
        "369702,5",
        "-1,4",
        "215072,20",
        "230552,222",
        "317404,9",
        "-1,1",
        "187905,25",
        "237958,25",
        "195554,57",
        "157049,31",
        "300024,26",
        "361309,30",
        "557889,30",
        "354829,31",
        "207988,25",
        "12493,180",
        "84408,188",
        "275202,100",
        "269493,82",
        "148726,141",
        "429340,26",
        "221479,50",
        "536829,31",
        "294810,957",
        "119276,101",
        "146577,100",
        "305935,25",
        "42275,7",
        "173536,25",
        "96088,13",
        "39414,30",
        "387739,5",
        "76169,191",
        "323276,25",
        "171308,25",
        "302861,32",
        "-1,0",
        "47049,58",
        "16001,12",
        "137073,20",
        "156367,159",
        "109276,36",
        "183842,100",
        "84942,70",
        "11074,1012",
        "68915,267",
        "13116,644",
        "71283,49",
        "-1,0",
        "70034,1028",
        "161669,35",
        "107994,42",
        "98483,1",
        "246086,5",
        "23108,1316",
        "42174,300",
        "-1,1",
        "167898,555",
        "670822,168",
        "21849,500",
        "259159,25",
        "346878,161",
    ]

    player_record = PlayerRecord("TestUser", csv, datetime(2025, 11, 16))

    assert player_record.username == "TestUser"
    assert player_record.rank == 271397
    assert player_record.total_level == 2084
    assert player_record.total_xp == 297498066
    assert math.isclose(player_record.combat_lvl, 125.35)

    skills_true = [
        HSType.attack, HSType.defence, HSType.strength, HSType.hitpoints, HSType.ranged,
        HSType.prayer, HSType.magic, HSType.cooking, HSType.woodcutting, HSType.fletching,
        HSType.fishing, HSType.firemaking, HSType.crafting, HSType.smithing, HSType.mining,
        HSType.herblore, HSType.agility, HSType.thieving, HSType.slayer, HSType.farming,
        HSType.runecrafting, HSType.hunter, HSType.construction, HSType.sailing,
    ]
    assert all(skill.name in player_record.skills for skill in skills_true)

    skills_false = []
    assert all(skill.name not in player_record.skills for skill in skills_false)

    minigames_true = [
        HSType.lms_rank, HSType.rifts_closed, HSType.colosseum_glory, HSType.collections_logged,
        HSType.pvp_arena_rank
    ]
    assert all(mg.name in player_record.misc for mg in minigames_true)

    minigames_false = [
        HSType.grid_points, HSType.league_points, HSType.dmm, HSType.bh_hunter, HSType.bh_rogue,
        HSType.bh_legacy_hunter, HSType.bh_legacy_rogue, HSType.sw_zeal
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

        HSType.callisto, HSType.calvarion, HSType.cerberus, HSType.cox, HSType.cox_cm, HSType.chaos_elemental,
        HSType.chaos_fanatic, HSType.saradomin, HSType.corp, HSType.crazy_archaeologist,

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

        HSType.vardorvis, HSType.venenatis, HSType.vetion, HSType.vorkath,
        HSType.wt, HSType.yama, HSType.zalcano, HSType.zulrah
    ]
    assert all(boss.name in player_record.misc for boss in bosses_true)

    bosses_false = [
        HSType.hmt,
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
