import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osrs_hiscore_scrape.exception.records import NotFound, RetryFailed
from osrs_hiscore_scrape.job.records import JobManager, JobQueue
from osrs_hiscore_scrape.worker.records import Worker, create_workers


@pytest.mark.asyncio
async def test_run_successful_job_processing(sample_fake_client_session):
    in_q = JobQueue()
    out_q = JobQueue()
    job_manager = JobManager(0, 0)

    mock_job = MagicMock()
    mock_job.priority = 0
    mock_job.result = None

    await in_q.put(mock_job)

    async def request_fn(req, job):
        job.result = "ok"

    async def enqueue_fn(out_q, job):
        await out_q.put(job)

    worker = Worker(
        req=sample_fake_client_session,
        in_queue=in_q,
        out_queue=out_q,
        job_manager=job_manager,
        request_fn=request_fn,
        enqueue_fn=enqueue_fn
    )

    async def stopper():
        await asyncio.sleep(0.05)
        await job_manager.await_until_finished()

    asyncio.create_task(stopper())
    await worker.run()

    result = await out_q.get()
    assert result.result == "ok"
    assert job_manager.value == 1


@pytest.mark.asyncio
async def test_run_not_found_increments_counter(sample_fake_client_session):
    in_q = JobQueue()
    out_q = JobQueue()
    job_manager = JobManager(0, 0)

    mock_job = MagicMock()
    mock_job.priority = 0
    mock_job.result = None

    await in_q.put(mock_job)

    async def request_fn(req, job):
        raise NotFound("not found")

    async def enqueue_fn(out_q, job):
        await out_q.put(job)

    worker = Worker(
        req=sample_fake_client_session,
        in_queue=in_q,
        out_queue=out_q,
        job_manager=job_manager,
        request_fn=request_fn,
        enqueue_fn=enqueue_fn
    )

    async def stopper():
        await asyncio.sleep(0.05)
        await job_manager.await_until_finished()

    asyncio.create_task(stopper())
    await worker.run()

    assert len(in_q) == 0
    assert job_manager.value == 1


@pytest.mark.asyncio
async def test_run_retry_failed_requeues_and_raises(sample_fake_client_session):
    in_q = JobQueue()
    out_q = JobQueue()
    job_manager = JobManager(0, 0)

    mock_job = MagicMock()
    mock_job.priority = 0
    mock_job.result = None

    await in_q.put(mock_job)

    async def request_fn(req, job):
        pass

    async def enqueue_fn(out_q, job):
        await out_q.put(job)

    worker = Worker(
        req=sample_fake_client_session,
        in_queue=in_q,
        out_queue=out_q,
        job_manager=job_manager,
        request_fn=request_fn,
        enqueue_fn=enqueue_fn
    )

    with (
        patch("osrs_hiscore_scrape.worker.records.retry", new=AsyncMock(
            side_effect=RetryFailed("retry failed"))),
        pytest.raises(RetryFailed)
    ):
        await worker.run(skip_failed=False)

    queued_again = await in_q.get()
    assert queued_again is mock_job


@pytest.mark.asyncio
async def test_run_retry_failed_moves_on(sample_fake_client_session):
    in_q = JobQueue()
    out_q = JobQueue()
    job_manager = JobManager(0, 0)

    mock_job = MagicMock()
    mock_job.priority = 0
    mock_job.result = None

    await in_q.put(mock_job)

    async def request_fn(req, job):
        pass

    async def enqueue_fn(out_q, job):
        await out_q.put(job)

    worker = Worker(
        req=sample_fake_client_session,
        in_queue=in_q,
        out_queue=out_q,
        job_manager=job_manager,
        request_fn=request_fn,
        enqueue_fn=enqueue_fn
    )

    with (
        patch("osrs_hiscore_scrape.worker.records.retry", new=AsyncMock(
            side_effect=RetryFailed("retry failed")))
    ):
        await worker.run(skip_failed=True)

    assert len(in_q) == 0
    assert job_manager.value == 1


def test_create_workers_args_passed():
    req = MagicMock()
    in_queue = MagicMock()
    out_queue = MagicMock()
    job_manager = MagicMock()
    request_fn = MagicMock()
    enqueue_fn = MagicMock()

    with patch("osrs_hiscore_scrape.worker.records.Worker") as MockWorker:
        workers = create_workers(
            req=req,
            in_queue=in_queue,
            out_queue=out_queue,
            job_manager=job_manager,
            request_fn=request_fn,
            enqueue_fn=enqueue_fn,
            num_workers=3,
        )

        assert len(workers) == 3
        assert MockWorker.call_count == 3


def test_create_workers_zero():
    with patch("osrs_hiscore_scrape.worker.records.Worker") as MockWorker:
        workers = create_workers(
            req=None,  # type: ignore
            in_queue=None,  # type: ignore
            out_queue=None,  # type: ignore
            job_manager=None,  # type: ignore
            request_fn=None,  # type: ignore
            enqueue_fn=None,  # type: ignore
            num_workers=0,
        )

        assert workers == []
        MockWorker.assert_not_called()
