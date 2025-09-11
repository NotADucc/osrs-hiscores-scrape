import math
import pytest
from datetime import datetime

from src.request.common import HSType
from src.request.dto import HSFilterEntry
from src.request.results import CategoryRecord, PlayerRecord



@pytest.fixture
def sample_csv() -> list[str]:
    return ["1,50,101333" if hs_type else "1,50" for hs_type in list(HSType)[:-1]]

@pytest.fixture
def sample_csv_incomplete() -> list[str]:
    return ["-1,1,-1" if hs_type else "-1,1" for hs_type in list(HSType)[:-1]]

@pytest.fixture
def player(sample_csv: list[str]) -> PlayerRecord:
    return PlayerRecord("TestUser", sample_csv, datetime(2023, 1, 1))

@pytest.fixture
def player_incomplete(sample_csv_incomplete: list[str]) -> PlayerRecord:
    return PlayerRecord("TestUser", sample_csv_incomplete, datetime(2023, 1, 1))

def test_player_record_initialization(player: PlayerRecord):
    assert player.username == "TestUser"
    assert player.rank == 1
    assert player.total_level == 50
    assert player.total_xp == 101333
    
    for hs_type in list(HSType)[1:-1]:
        if hs_type.is_skill():
            assert hs_type.name in player.skills
        else :
            assert hs_type.name in player.misc

    assert math.isclose(player.combat_lvl, 63.75)


def tes_player_record_get_stat_overall(player: PlayerRecord):
    assert player.get_stat(HSType.overall) == player.total_level


def test_player_record_get_stat_combat(player: PlayerRecord):
    assert player.get_stat(HSType.combat) == player.combat_lvl


def test_player_record_get_stat_skill(player: PlayerRecord):
    for hs_type in list(HSType)[1:-1]:
        if hs_type.is_skill():
            skill_lvl = player.skills[hs_type.name]
            assert player.get_stat(hs_type=hs_type) == skill_lvl


def test_player_record_get_stat_misc_returns_default(player_incomplete: PlayerRecord):
    some_misc = next(h for h in HSType if h.is_misc())
    assert player_incomplete.get_stat(some_misc) in (0, player_incomplete.misc.get(some_misc.name, 0))


def test_player_record_meets_and_lacks_requirements(player: PlayerRecord):
    req = HSFilterEntry(HSType.attack, lambda v: v >= 50)
    assert player.meets_requirements([req])
    assert not player.lacks_requirements([req])

    req_fail = HSFilterEntry(HSType.attack, lambda v: v > 99)
    assert not player.meets_requirements([req_fail])
    assert player.lacks_requirements([req_fail])


def test_player_record_ordering(player: PlayerRecord, sample_csv):
    better_total = PlayerRecord("BetterTotal", sample_csv, datetime(2023, 1, 1))
    better_total.total_level = player.total_level + 1

    assert player < better_total
    assert better_total > player
    assert not (player == better_total)


def test_player_record_eq_same_values(player: PlayerRecord, sample_csv: list[str]):
    copy = PlayerRecord("TestUser", sample_csv, datetime(2023, 1, 1))
    copy.total_level = player.total_level
    copy.total_xp = player.total_xp
    copy.rank = player.rank

    assert player == copy


def test_player_record_to_and_from_dict(player: PlayerRecord):
    d = player.to_dict()
    restored = PlayerRecord.from_dict(d)

    assert restored.username == player.username
    assert restored.total_level == player.total_level
    assert restored.skills == player.skills
    assert restored.misc == player.misc


def test_player_record_str_returns_json(player: PlayerRecord):
    s = str(player)
    assert s.startswith("{")
    assert '"username":"TestUser"' in s
    for hs_type in list(HSType)[1:]:
        assert hs_type.name in s


@pytest.fixture
def record():
    return CategoryRecord(rank=1, score=5000, username="PlayerOne")


@pytest.fixture
def worse_record():
    return CategoryRecord(rank=10, score=3000, username="PlayerTwo")


def test_category_record_initialization(record: CategoryRecord):
    assert record.rank == 1
    assert record.score == 5000
    assert record.username == "PlayerOne"


def test_category_record_is_better_rank_than(record: CategoryRecord, worse_record: CategoryRecord):
    assert record.is_better_rank_than(worse_record) is True
    assert worse_record.is_better_rank_than(record) is False
    assert record.is_better_rank_than(None) is False # type: ignore


def test_category_record_is_worse_rank_than(record: CategoryRecord, worse_record: CategoryRecord):
    assert worse_record.is_worse_rank_than(record) is True
    assert record.is_worse_rank_than(worse_record) is False
    assert record.is_worse_rank_than(None) is False # type: ignore


def test_category_record_to_dict(record: CategoryRecord):
    d = record.to_dict()
    assert d == {"rank": 1, "score": 5000, "username": "PlayerOne"}


def test_category_record_ordering_lt(record: CategoryRecord, worse_record: CategoryRecord):
    # lower rank is better
    assert record < worse_record
    assert not worse_record < record


def test_category_record_equality(record: CategoryRecord):
    same_rank_diff_user = CategoryRecord(rank=1, score=100, username="Other")
    diff_rank = CategoryRecord(rank=2, score=5000, username="Other")

    assert record == same_rank_diff_user
    assert record != diff_rank
    assert not record == None  
    assert record != None  


def test_category_record_str_returns_json(record: CategoryRecord):
    s = str(record)
    assert s.startswith("{")
    assert '"rank":1' in s
    assert '"score":5000' in s
    assert '"username":"PlayerOne"' in s