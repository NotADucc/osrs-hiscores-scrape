from src.request.results import CategoryRecord


def test_initialization(sample_category_record: CategoryRecord):
    assert sample_category_record.rank == 1
    assert sample_category_record.score == 5000
    assert sample_category_record.username == "PlayerOne"


def test_is_better_rank_than(sample_category_record: CategoryRecord, sample_category_record_worse_rank: CategoryRecord):
    assert sample_category_record.is_better_rank_than(
        sample_category_record_worse_rank) is True
    assert sample_category_record_worse_rank.is_better_rank_than(
        sample_category_record) is False
    assert sample_category_record.is_better_rank_than(
        None) is False  # type: ignore


def test_is_worse_rank_than(sample_category_record: CategoryRecord, sample_category_record_worse_rank: CategoryRecord):
    assert sample_category_record_worse_rank.is_worse_rank_than(
        sample_category_record) is True
    assert sample_category_record.is_worse_rank_than(
        sample_category_record_worse_rank) is False
    assert sample_category_record.is_worse_rank_than(
        None) is False  # type: ignore


def test_to_dict(sample_category_record: CategoryRecord):
    d = sample_category_record.to_dict()
    assert d == {"rank": 1, "score": 5000, "username": "PlayerOne"}


def test_ordering_lt(sample_category_record: CategoryRecord, sample_category_record_worse_rank: CategoryRecord):
    # lower rank is better
    assert sample_category_record < sample_category_record_worse_rank
    assert not sample_category_record_worse_rank < sample_category_record


def test_equality(sample_category_record: CategoryRecord):
    same_rank_diff_user = CategoryRecord(rank=1, score=100, username="Other")
    diff_rank = CategoryRecord(rank=2, score=5000, username="Other")

    assert sample_category_record == same_rank_diff_user
    assert sample_category_record != diff_rank
    assert not sample_category_record == None
    assert sample_category_record != None


def test_str_returns_json(sample_category_record: CategoryRecord):
    s = str(sample_category_record)
    assert s.startswith("{")
    assert '"rank":1' in s
    assert '"score":5000' in s
    assert '"username":"PlayerOne"' in s
