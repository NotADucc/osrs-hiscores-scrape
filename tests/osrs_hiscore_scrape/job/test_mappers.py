from osrs_hiscore_scrape.job.mappers import (
    map_category_record_to_lookup_job, map_category_records_to_lookup_jobs,
    map_player_record_to_lookup_job, map_player_records_to_lookup_jobs)
from osrs_hiscore_scrape.job.records import HSLookupJob
from osrs_hiscore_scrape.request.hs_types import HSAccountTypes
from osrs_hiscore_scrape.request.records import CategoryRecord, PlayerRecord


def test_map_player_record_to_lookup_job(sample_player_record: PlayerRecord):
    job = map_player_record_to_lookup_job(
        priority=1, account_type=HSAccountTypes.regular, input=sample_player_record)

    assert isinstance(job, HSLookupJob)
    assert job.priority == 1
    assert job.account_type == HSAccountTypes.regular
    assert job.username == sample_player_record.username
    assert not job.result


def test_map_player_records_to_lookup_jobs_empty():
    jobs = map_player_records_to_lookup_jobs(
        account_type=HSAccountTypes.regular, input=[])
    assert jobs == []


def test_map_player_records_to_lookup_jobs_multiple(sample_player_records: list[PlayerRecord]):
    jobs = map_player_records_to_lookup_jobs(
        account_type=HSAccountTypes.regular, input=sample_player_records)

    assert len(jobs) == len(sample_player_records)
    for idx, job in enumerate(jobs):
        assert job.priority == idx
        assert job.username == sample_player_records[idx].username
        assert not job.result


def test_map_category_record_to_lookup_job(sample_category_record: CategoryRecord):
    job = map_category_record_to_lookup_job(
        priority=5, account_type=HSAccountTypes.regular, input=sample_category_record)

    assert isinstance(job, HSLookupJob)
    assert job.priority == 5
    assert job.account_type == HSAccountTypes.regular
    assert job.username == sample_category_record.username
    assert not job.result


def test_map_category_records_to_lookup_jobs_empty():
    jobs = map_category_records_to_lookup_jobs(
        account_type=HSAccountTypes.regular, input=[])
    assert jobs == []


def test_map_category_records_to_lookup_jobs_multiple(sample_category_records: list[CategoryRecord]):
    jobs = map_category_records_to_lookup_jobs(
        account_type=HSAccountTypes.regular, input=sample_category_records)

    assert len(jobs) == len(sample_category_records)
    for idx, job in enumerate(jobs):
        assert job.priority == idx
        assert job.account_type == HSAccountTypes.regular
        assert job.username == sample_category_records[idx].username
        assert not job.result
