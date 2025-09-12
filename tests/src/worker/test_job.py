import asyncio
import pytest
from dataclasses import fields

# Assuming these are imported from your module
# from your_module import IJob, HSCategoryJob, HSLookupJob, HSAccountTypes, HSType, PlayerRecord, CategoryRecord

# ---- Dummy classes for testing (replace with real ones) ----
from enum import Enum
from dataclasses import dataclass

from src.request.common import HSAccountTypes, HSType
from src.request.results import CategoryRecord, PlayerRecord
from src.worker.job import HSCategoryJob, HSLookupJob, JobManager, JobQueue


def test_hslookupjob_initialization_defaults():
    job = HSLookupJob(priority=1, username="alice", account_type=HSAccountTypes.regular)

    assert job.priority == 1
    assert job.username == "alice"
    assert job.account_type == HSAccountTypes.regular
    assert job.result is None  # default should be None


def test_hslookupjob_with_result(sample_player_record: PlayerRecord):
    job = HSLookupJob(priority=2, username="alice", account_type=HSAccountTypes.im, result=sample_player_record)

    assert job.result == sample_player_record
    assert isinstance(job.result, PlayerRecord)


def test_hslookupjob_ordering_by_priority():
    job1 = HSLookupJob(priority=1, username="bob", account_type=HSAccountTypes.regular)
    job2 = HSLookupJob(priority=2, username="carol", account_type=HSAccountTypes.regular)

    assert job1 < job2
    assert sorted([job2, job1]) == [job1, job2]


def test_hscategoryjob_initialization_defaults():
    job = HSCategoryJob(
        priority=3,
        page_num=1,
        start_rank=1,
        end_rank=25,
        hs_type=HSType.overall,
        account_type=HSAccountTypes.im,
        start_idx=0,
        end_idx=25,
    )

    assert job.priority == 3
    assert job.page_num == 1
    assert job.start_rank == 1
    assert job.end_rank == 25
    assert job.hs_type == HSType.overall
    assert job.account_type == HSAccountTypes.im
    assert job.start_idx == 0
    assert job.end_idx == 25
    assert job.result is None


def test_hscategoryjob_with_result(sample_category_records: list[CategoryRecord]):
    job = HSCategoryJob(
        priority=5,
        page_num=2,
        start_rank=26,
        end_rank=50,
        hs_type=HSType.overall,
        account_type=HSAccountTypes.regular,
        start_idx=25,
        end_idx=50,
        result=sample_category_records,
    )

    assert job.result == sample_category_records
    assert all(isinstance(r, CategoryRecord) for r in job.result)


def test_hscategoryjob_ordering_by_priority():
    job1 = HSCategoryJob(
        priority=1, page_num=1, start_rank=1, end_rank=25,
        hs_type=HSType.overall, account_type=HSAccountTypes.regular,
        start_idx=0, end_idx=25,
    )
    job2 = HSCategoryJob(
        priority=2, page_num=2, start_rank=26, end_rank=50,
        hs_type=HSType.overall, account_type=HSAccountTypes.regular,
        start_idx=25, end_idx=50,
    )

    assert job1 < job2
    assert sorted([job2, job1]) == [job1, job2]


def test_dataclass_fields_match_expected():
    """Ensure all expected fields exist in the dataclasses."""
    lookup_fields = {f.name for f in fields(HSLookupJob)}
    category_fields = {f.name for f in fields(HSCategoryJob)}

    assert {"priority", "username", "account_type", "result"}.issubset(lookup_fields)
    assert {"priority", "page_num", "start_rank", "end_rank",
            "hs_type", "account_type", "start_idx", "end_idx", "result"}.issubset(category_fields)


@pytest.mark.asyncio
async def test_jobmanager_initial_state():
    jm = JobManager(start=0, end=3)

    assert jm.value == 0
    assert jm.is_finished() is False


@pytest.mark.asyncio
async def test_jobmanager_set_and_next_triggers_events():
    jm = JobManager(start=0, end=2)

    async def waiter():
        await jm.await_next()
        return jm.value

    task = asyncio.create_task(waiter())

    jm.next()
    val = await asyncio.wait_for(task, timeout=1)

    assert val == 1
    assert jm.value == 1
    assert jm.is_finished() is False

    jm.set(3)
    assert jm.is_finished() is True
    await jm.await_until_finished() 


@pytest.mark.asyncio
async def test_jobmanager_finished_immediately():
    jm = JobManager(start=5, end=3)
    assert jm.is_finished() is True

    await jm.await_next()
    await jm.await_until_finished()


@pytest.mark.asyncio
async def test_jobqueue_put_and_get_basic():
    q = JobQueue()

    await q.put((1, "a"))
    await q.put((0, "b"))

    assert len(q) == 2

    first = await q.get()
    second = await q.get()

    assert first[1] == "b" 
    assert second[1] == "a"


@pytest.mark.asyncio
async def test_jobqueue_peek_and_last():
    q = JobQueue()

    await q.put((2, "x"))
    await q.put((1, "y"))

    assert q.peek()[1] == "y"  
    assert q.last()[1] == "x"   


@pytest.mark.asyncio
async def test_jobqueue_peek_and_last_empty():
    q = JobQueue()

    with pytest.raises(asyncio.QueueEmpty):
        q.peek()

    with pytest.raises(asyncio.QueueEmpty):
        q.last()


@pytest.mark.asyncio
async def test_jobqueue_maxsize_blocks_until_get():
    q = JobQueue(maxsize=1)

    await q.put((1, "only"))

    async def try_put():
        await q.put((0, "second"))

    task = asyncio.create_task(try_put())

    await asyncio.sleep(0.1)
    assert not task.done()

    await q.get()
    await asyncio.wait_for(task, timeout=1)

    assert len(q) == 1