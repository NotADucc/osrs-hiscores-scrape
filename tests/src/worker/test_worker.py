import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.request.errors import NotFound, RetryFailed
from src.worker.job import JobManager, JobQueue
from src.worker.worker import Worker


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
        patch("src.worker.worker.retry", new=AsyncMock(side_effect=RetryFailed("retry failed"))),
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
        patch("src.worker.worker.retry", new=AsyncMock(side_effect=RetryFailed("retry failed")))
    ):
        await worker.run(skip_failed=True)

    assert len(in_q) == 0
    assert job_manager.value == 1