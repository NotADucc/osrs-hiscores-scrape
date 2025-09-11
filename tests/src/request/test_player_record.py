import math
from datetime import datetime

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.request.results import PlayerRecord


def test_initialization(sample_player_record: PlayerRecord):
    assert sample_player_record.username == "TestUser"
    assert sample_player_record.rank == 1
    assert sample_player_record.total_level == 50
    assert sample_player_record.total_xp == 101333

    for hs_type in list(HSType)[1:-1]:
        if hs_type.is_skill():
            assert hs_type.name in sample_player_record.skills
        else:
            assert hs_type.name in sample_player_record.misc

    assert math.isclose(sample_player_record.combat_lvl, 63.75)


def tes_get_stat_overall(sample_player_record: PlayerRecord):
    assert sample_player_record.get_stat(
        HSType.overall) == sample_player_record.total_level


def test_get_stat_combat(sample_player_record: PlayerRecord):
    assert sample_player_record.get_stat(
        HSType.combat) == sample_player_record.combat_lvl


def test_get_stat_skill(sample_player_record: PlayerRecord):
    for hs_type in list(HSType)[1:-1]:
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
    for hs_type in list(HSType)[1:]:
        assert hs_type.name in s
