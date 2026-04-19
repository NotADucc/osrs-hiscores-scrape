import math
from datetime import datetime

from osrs_hiscore_scrape.request.dto import HSFilterEntry
from osrs_hiscore_scrape.request.hs_types import HSType
from osrs_hiscore_scrape.request.records import (PlayerRecord,
                                                 PlayerRecordSkillInfo)
from osrs_hiscore_scrape.statistic.calculators import calc_combat_level


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
        "57729,688",
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
    assert math.isclose(player_record.combat_lvl.value, 125.35)

    skills = [
        HSType.overall, HSType.sailing,
    ]
    assert all(skill.name in player_record.skills for skill in skills)

    minigames = [
        HSType.lms_rank, HSType.rifts_closed, HSType.pvp_arena_rank,
        HSType.bh_hunter, HSType.bh_rogue, HSType.bh_legacy_hunter,
        HSType.bh_legacy_rogue, HSType.sw_zeal
    ]
    assert all(mg.name in player_record.minigames for mg in minigames)

    seasonal_modes = [
        HSType.grid_points, HSType.league_points, HSType.dmm
    ]
    assert all(sm.name in player_record.seasonal_modes for sm in seasonal_modes)

    clues = [
        HSType.clue_all, HSType.clue_master
    ]
    assert all(clue.name in player_record.clues for clue in clues)

    misc = [
        HSType.colosseum_glory, HSType.collections_logged,
    ]
    assert all(misc.name in player_record.misc for misc in misc)

    bosses = [
        HSType.sire, HSType.zulrah
    ]
    assert all(boss.name in player_record.bosses for boss in bosses)


def test_initialization_incomplete_csv():
    csv = [
        "268860,2084,295930696",
    ]
    player_record = PlayerRecord("TestUser", csv, datetime(2025, 11, 3))

    assert player_record.username == "TestUser"
    assert math.isclose(player_record.combat_lvl.value, 3)

    assert not player_record.skills
    assert not player_record.seasonal_modes
    assert not player_record.minigames
    assert not player_record.clues
    assert not player_record.misc
    assert not player_record.bosses


def test_get_stat_combat(sample_player_record: PlayerRecord):
    assert sample_player_record.get_stat(
        HSType.combat) == sample_player_record.combat_lvl


def test_get_stat_skill(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_skill():
            result = sample_player_record.skills[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_seasonal_modes(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_seasonal_mode():
            result = sample_player_record.seasonal_modes[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_clues(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_clue():
            result = sample_player_record.clues[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_minigames(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_minigame():
            result = sample_player_record.minigames[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_bosses(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_boss():
            result = sample_player_record.bosses[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_misc(sample_player_record: PlayerRecord):
    for hs_type in HSType.get_csv_types():
        if hs_type.is_misc():
            result = sample_player_record.misc[hs_type.name]
            assert sample_player_record.get_stat(hs_type=hs_type) == result


def test_get_stat_misc_returns_default(sample_player_record_incomplete: PlayerRecord):
    some_misc = next(h for h in HSType if h.is_misc())
    assert sample_player_record_incomplete.get_stat(some_misc) in (
        0, sample_player_record_incomplete.misc.get(some_misc.name, 0))


def test_meets_and_lacks_requirements():
    player_record = PlayerRecord("test", ["1,50,101333" if hs_type.is_skill(
    ) else "1,50" for hs_type in HSType.get_csv_types()], datetime(2023, 1, 1))
    expected_cmb_lvl = calc_combat_level(
        attack=50,
        defence=50,
        strength=50,
        hitpoints=50,
        ranged=50,
        prayer=50,
        magic=50
    )

    req_overall = HSFilterEntry(HSType.overall, lambda v: v >= 50)
    assert player_record.meets_requirements([req_overall])
    assert not player_record.lacks_requirements([req_overall])

    req_overall_fail = HSFilterEntry(HSType.overall, lambda v: v > 50)
    assert not player_record.meets_requirements([req_overall_fail])
    assert player_record.lacks_requirements([req_overall_fail])

    req_cmb = HSFilterEntry(HSType.combat, lambda v: v >= expected_cmb_lvl)
    assert player_record.meets_requirements([req_cmb])
    assert not player_record.lacks_requirements([req_cmb])

    req_cmb_fail = HSFilterEntry(HSType.combat, lambda v: v > expected_cmb_lvl)
    assert not player_record.meets_requirements([req_cmb_fail])
    assert player_record.lacks_requirements([req_cmb_fail])

    req_skill = HSFilterEntry(HSType.attack, lambda v: v >= 50)
    assert player_record.meets_requirements([req_skill])
    assert not player_record.lacks_requirements([req_skill])

    req_skill_fail = HSFilterEntry(HSType.attack, lambda v: v > 99)
    assert not player_record.meets_requirements([req_skill_fail])
    assert player_record.lacks_requirements([req_skill_fail])

    req_misc = HSFilterEntry(HSType.zuk, lambda v: v >= 50)
    assert player_record.meets_requirements([req_misc])
    assert not player_record.lacks_requirements([req_misc])

    req_misc_fail = HSFilterEntry(HSType.zuk, lambda v: v > 50)
    assert not player_record.meets_requirements([req_misc_fail])
    assert player_record.lacks_requirements([req_misc_fail])


def test_ordering(sample_player_record: PlayerRecord, sample_player_record_csv_list: list[str], sample_ts: datetime):
    better_record = PlayerRecord(
        "BetterTotal", sample_player_record_csv_list, sample_ts)

    sample_total = sample_player_record.get_stat(hs_type=HSType.overall)
    better_total = better_record.get_stat(hs_type=HSType.overall)

    assert isinstance(sample_total, PlayerRecordSkillInfo)
    assert isinstance(better_total, PlayerRecordSkillInfo)

    better_total.lvl = sample_total.lvl + 1

    assert sample_player_record < better_record
    assert better_record > sample_player_record
    assert not (sample_player_record == better_record)


def test_eq_same_values(sample_player_record: PlayerRecord, sample_player_record_csv_list: list[str], sample_ts: datetime):
    copy = PlayerRecord("TestUser", sample_player_record_csv_list, sample_ts)

    sample_total = sample_player_record.get_stat(hs_type=HSType.overall)
    copy_total = copy.get_stat(hs_type=HSType.overall)

    assert isinstance(sample_total, PlayerRecordSkillInfo)
    assert isinstance(copy_total, PlayerRecordSkillInfo)

    copy_total.lvl = sample_total.lvl
    copy_total.xp = sample_total.xp
    copy_total.rank = sample_total.rank

    assert sample_player_record == copy


def test_to_and_from_dict(sample_player_record: PlayerRecord):
    d = sample_player_record.to_dict()
    restored = PlayerRecord.from_dict(d)

    assert restored.username == sample_player_record.username
    assert restored.combat_lvl == sample_player_record.combat_lvl

    assert restored.skills == sample_player_record.skills
    assert restored.seasonal_modes == sample_player_record.seasonal_modes
    assert restored.clues == sample_player_record.clues
    assert restored.minigames == sample_player_record.minigames
    assert restored.bosses == sample_player_record.bosses
    assert restored.misc == sample_player_record.misc


def test_str_returns_json(sample_player_record: PlayerRecord):
    s = str(sample_player_record)
    assert s.startswith("{")
    assert '"username":"TestUser"' in s
    for hs_type in HSType.get_csv_types()[1:]:
        assert hs_type.name in s
