import pytest

from src.request.results import CategoryRecord


@pytest.fixture
def record():
    return CategoryRecord(rank=1, score=5000, username="PlayerOne")


@pytest.fixture
def worse_record():
    return CategoryRecord(rank=10, score=3000, username="PlayerTwo")


def test_initialization(record: CategoryRecord):
    assert record.rank == 1
    assert record.score == 5000
    assert record.username == "PlayerOne"


def test_is_better_rank_than(record: CategoryRecord, worse_record: CategoryRecord):
    assert record.is_better_rank_than(worse_record) is True
    assert worse_record.is_better_rank_than(record) is False
    assert record.is_better_rank_than(None) is False  # type: ignore


def test_is_worse_rank_than(record: CategoryRecord, worse_record: CategoryRecord):
    assert worse_record.is_worse_rank_than(record) is True
    assert record.is_worse_rank_than(worse_record) is False
    assert record.is_worse_rank_than(None) is False  # type: ignore


def test_to_dict(record: CategoryRecord):
    d = record.to_dict()
    assert d == {"rank": 1, "score": 5000, "username": "PlayerOne"}


def test_ordering_lt(record: CategoryRecord, worse_record: CategoryRecord):
    # lower rank is better
    assert record < worse_record
    assert not worse_record < record


def test_equality(record: CategoryRecord):
    same_rank_diff_user = CategoryRecord(rank=1, score=100, username="Other")
    diff_rank = CategoryRecord(rank=2, score=5000, username="Other")

    assert record == same_rank_diff_user
    assert record != diff_rank
    assert not record == None
    assert record != None


def test_str_returns_json(record: CategoryRecord):
    s = str(record)
    assert s.startswith("{")
    assert '"rank":1' in s
    assert '"score":5000' in s
    assert '"username":"PlayerOne"' in s
