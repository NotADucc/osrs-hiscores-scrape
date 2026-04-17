import asyncio
from asyncio import CancelledError, Queue
from typing import Callable

from ..exception.records import NotFound, RetryFailed
from ..job.records import IJob, JobManager, JobQueue
from ..request.request import Requests
from ..util.retry_handler import retry

# there is a design bug, well i see it as a bug
# when using 2 workers that are dependant on eachother, lets say 'master' and 'slave'
# when the master skips a record, the slave has no idea about that since
# the master JobManager gets skipped but the slave's doesn't
# it's already an issue #16
# no clue if i should actually account for that edge case
# or just leave it be


class Worker:
    """
    Represents an asynchronous worker that processes jobs from an input queue
    and forwards results to an output queue, coordinating execution via a JobCounter.

    The worker continuously fetches jobs from `in_queue`, executes a request
    function on each job, waits for its turn based on the job's priority, and
    then enqueues the result using a provided enqueue function.
    """

    def __init__(
        self,
        req: Requests,
        in_queue: JobQueue[IJob],
        out_queue: Queue[IJob] | JobQueue[IJob],
        job_manager: JobManager,
        request_fn: Callable,
        enqueue_fn: Callable,
    ):
        self.req = req
        self.in_q = in_queue
        self.out_q = out_queue
        self.job_manager = job_manager
        self.request_fn = request_fn
        self.enqueue_fn = enqueue_fn

    async def run(self, initial_delay: float = 0, max_retries: int = 10, skip_failed: bool = False) -> None:
        """            
        Continuously process jobs from the input queue:
            1. Optionally wait for an initial delay.
            2. Retrieve a job from the input queue.
            3. Execute `request_fn` on the job if its result is None, with retry handling.
            4. Wait until `job_counter` reaches the job's priority.
            5. Enqueue the processed job using `enqueue_fn`.
            6. Increment the `job_counter`.

        Exceptions Handled:
            NotFound: Simply increments the job counter and continues.
            CancelledError, RetryFailed: Requeues the job forcibly and re-raises the exception.
        """
        while not self.job_manager.is_finished():
            await asyncio.sleep(initial_delay)

            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(self.in_q.get()),
                    asyncio.create_task(
                        self.job_manager.await_until_finished()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()

            job = next(iter(done)).result()

            if not job:
                continue

            try:
                if job.result is None:
                    await retry(self.request_fn, req=self.req, job=job, max_retries=max_retries)

                while self.job_manager.value < job.priority:
                    await self.job_manager.await_next()

                await self.enqueue_fn(self.out_q, job)
                self.job_manager.next()

            except NotFound:
                self.job_manager.next()
            except (CancelledError, RetryFailed):
                if skip_failed:
                    self.job_manager.next()
                else:
                    await self.in_q.put(job, force=True)
                    raise


def create_workers(
    req: Requests,
    in_queue: JobQueue[IJob],
    out_queue: Queue[IJob] | JobQueue[IJob],
    job_manager: JobManager,
    request_fn: Callable,
    enqueue_fn: Callable,
    num_workers: int
):
    return [Worker(req=req, request_fn=request_fn, enqueue_fn=enqueue_fn, in_queue=in_queue, out_queue=out_queue, job_manager=job_manager)
            for _ in range(num_workers)]
