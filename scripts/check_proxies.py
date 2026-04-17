import argparse
import asyncio
import os
from dataclasses import dataclass

import aiohttp

from osrs_hiscore_scrape.exception.records import RequestFailed
from osrs_hiscore_scrape.job.records import IJob, JobManager, JobQueue
from osrs_hiscore_scrape.log.decorators import log_lifecycle
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util.io import read_proxies, write_records
from osrs_hiscore_scrape.util.script_utils import script_running_in_cmd_guard
from osrs_hiscore_scrape.worker.records import create_workers

logger = get_logger(__name__)

N_PROXY_WORKERS = 20


@dataclass(order=True)
class ProxyJob(IJob):
    priority: int
    proxy: str
    result: str = None  # type: ignore


async def request_proxy(req: Requests, job: ProxyJob):
    proxy = job.proxy

    if proxy.startswith(("https://", "http://", "socks4://", "socks5://")):
        proxy = proxy
    else:
        # ip, port, user, pwd
        splitted = proxy.split(":")
        proxy = f"http://{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}" \
            if len(splitted) > 2 \
            else f"http://{splitted[0]}:{splitted[1]}"

    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        async with session.get("http://httpbin.org/ip", proxy=proxy, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 200:
                logger.debug(f'OK: {await resp.json()}')
                job.result = proxy
            elif resp.status in (402, 403, 404):
                logger.error(
                    f"{proxy}, code:{resp.status}, reason:{resp.reason}")
            else:
                raise RequestFailed(f"failed proxy '{proxy}'", details={
                                    "code": resp.status, "reason": resp.reason, "url": resp.url})


async def enqueue_proxy(queue: JobQueue | asyncio.Queue, job: ProxyJob):
    await queue.put(job if job.result else None)


@log_lifecycle
async def main(proxy_file: str):
    potential_proxies = read_proxies(proxy_file=proxy_file)

    file_name = os.path.basename(proxy_file)
    base_proxy_file, ext = os.path.splitext(file_name)

    out_file = base_proxy_file + "_valid" + ext

    async with aiohttp.ClientSession() as session:
        req = Requests(session=session)

        proxy_job_q = JobQueue[IJob]()
        for idx, potential_proxie in enumerate(potential_proxies):
            await proxy_job_q.put(ProxyJob(priority=idx, proxy=potential_proxie))

        proxy_export = asyncio.Queue()
        proxy_job_manager = JobManager(start=1, end=len(potential_proxies))

        proxy_workers = create_workers(
            req=req,
            in_queue=proxy_job_q,
            out_queue=proxy_export,
            job_manager=proxy_job_manager,
            request_fn=request_proxy,
            enqueue_fn=enqueue_proxy,
            num_workers=N_PROXY_WORKERS
        )

        T = [asyncio.create_task(
            write_records(in_queue=proxy_export,
                          out_file=out_file,
                          total=len(potential_proxies),
                          format=lambda job: job.result)
        )]

        for i, w in enumerate(proxy_workers):
            T.append(asyncio.create_task(
                w.run(initial_delay=i * 0.1, max_retries=2, skip_failed=True)
            ))
        try:
            await asyncio.gather(*T)
        finally:
            for task in T:
                task.cancel()
            await asyncio.gather(*T, return_exceptions=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy-file', required=True,
                        help="Path to the proxy file")
    script_running_in_cmd_guard()

    args = parser.parse_args()

    asyncio.run(main(args.proxy_file))
