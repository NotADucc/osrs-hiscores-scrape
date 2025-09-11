from datetime import datetime

import pytest


from src.request.results import CategoryInfo, CategoryRecord

def test_initialization(sample_ts: datetime):
    category_info = CategoryInfo("category", sample_ts)

    assert category_info.name == "category"
    assert category_info.ts == sample_ts
    assert category_info.is_empty() is True
    assert category_info.max is None
    assert category_info.min is None
    assert category_info._total_score == 0


def test_add_updates_min_max_total(sample_ts: datetime, sample_category_records: list[CategoryRecord]):
    category_info = CategoryInfo("category", sample_ts)

    for rec in sample_category_records:
        category_info.add(rec)

    assert category_info.is_empty() is False
    assert category_info._total_score == sum(r.score for r in sample_category_records)
    assert category_info.max.username == "test1"    # type: ignore
    assert category_info.min.username == "test5"    # type: ignore
    assert len(category_info._records) == 5


def test_sort_caches_deltas(sample_ts: datetime, sample_category_records: list[CategoryRecord]):
    category_info = CategoryInfo("category", sample_ts)

    for rec in sample_category_records:
        category_info.add(rec)

    category_info._sort()
    assert category_info._is_sorted is True

    mean = sum(record.score for record in sample_category_records) / len(sample_category_records)

    assert category_info._cached_sum_squared_delta == sum(
        (record.score - mean) ** 2 for record in sample_category_records)
    assert category_info._cached_sum_cubed_delta == sum(
        (record.score - mean) ** 3 for record in sample_category_records)
    assert category_info._cached_sum_quartic_delta == sum(
        (record.score - mean) ** 4 for record in sample_category_records)


def test_to_dict_basic_stats(sample_ts: datetime, sample_category_records: list[CategoryRecord]):
    category_info = CategoryInfo("category", sample_ts)

    for rec in sample_category_records:
        category_info.add(rec)

    dct = category_info.to_dict()

    assert dct["name"] == "category"
    assert dct["timestamp"] == sample_ts.isoformat()
    assert dct["count"] == 5
    assert dct["total_score"] == 1010
    assert pytest.approx(dct["mean"]) == 202
    assert dct["median"] is not None
    assert "population" in dct
    assert "sample" in dct
    assert "quartiles" in dct
    assert dct["max"]["username"] == "test1"
    assert dct["min"]["username"] == "test5"


def test_to_dict_quartiles_and_iqr(sample_ts: datetime, sample_category_records: list[CategoryRecord]):
    category_info = CategoryInfo("category", sample_ts)

    for rec in sample_category_records:
        category_info.add(rec)

    dct = category_info.to_dict()
    q1, q2, q3 = dct["quartiles"]["q1"], dct["quartiles"]["q2"], dct["quartiles"]["q3"]

    assert q1 is not None
    assert q2 is not None
    assert q3 is not None
    assert dct["quartiles"]["iqr"] == pytest.approx(q3 - q1)


def test_to_dict_empty(sample_ts: datetime):
    category_info = CategoryInfo("category", sample_ts)

    dct = category_info.to_dict()

    assert dct["count"] == 0
    assert dct["mean"] is None
    assert dct["median"] is None
    assert dct["max"] is None
    assert dct["min"] is None
    assert dct["quartiles"]["q1"] is None
    assert dct["population"]["variance"] is None
    assert dct["sample"]["variance"] is None


def test_str_returns_json(sample_ts: datetime, sample_category_records: list[CategoryRecord]):
    category_info = CategoryInfo("category", sample_ts)

    for rec in sample_category_records:
        category_info.add(rec)

    s = str(category_info)
    assert s.startswith("{")
    assert '"name":"category"' in s
    assert '"count":5' in s
