import argparse
import asyncio
import re
import sys
from functools import partial
from typing import Callable

import aiohttp

from src.request.common import (DEFAULT_WORKER_SIZE, MAX_CATEGORY_SIZE,
                                HSAccountTypes, HSType)
from src.request.dto import GetFilteredPageRangeRequest
from src.request.errors import FinishedScript
from src.request.request import Requests
from src.util.benchmarking import benchmark
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.io import (filtered_result_formatter, read_filtered_result,
                         read_hs_records, read_proxies, write_records)
from src.util.log import finished_script, get_logger
from src.worker.job import (GetMaxHighscorePageRequest, HSCategoryJob, IJob,
                            JobManager, JobQueue, get_hs_filtered_job,
                            get_hs_page_job)
from src.worker.mappers import (map_category_records_to_lookup_jobs,
                                map_player_records_to_lookup_jobs)
from src.worker.worker import (Worker, create_workers, enqueue_page_usernames,
                               enqueue_user_stats_filter, request_hs_page,
                               request_user_stats)

logger = get_logger()
N_SCRAPE_WORKERS = 2
N_SCRAPE_SIZE = 100


async def prepare_scrape_jobs(req: Requests, in_file: str, start_rank: int, account_type: HSAccountTypes, hs_type: HSType, hs_filter: dict[HSType, Callable[[int | float], bool]]) -> tuple[list[HSCategoryJob], int, JobQueue[IJob]]:
    """ Prepares the scraping job list and export queue based if theres an in-file or not. """
    potential_records = map_category_records_to_lookup_jobs(
        account_type=account_type, input=list(read_hs_records(in_file)))

    if not potential_records:
        potential_records = map_player_records_to_lookup_jobs(
            account_type=account_type, input=list(read_filtered_result(in_file)))

    if potential_records:
        hs_scrape_export_q = JobQueue[IJob]()
        for record in potential_records:
            await hs_scrape_export_q.put(record)
        return [], len(potential_records), hs_scrape_export_q

    filtered = {k: v for k, v in hs_filter.items() if k == hs_type}

    if filtered:
        hs_scrape_joblist, start_job_prio, end_job_prio = [], 1, MAX_CATEGORY_SIZE

        for pred in filtered.values():
            temp_joblist = await get_hs_filtered_job(req=req,
                                                     start_rank=start_rank,
                                                     end_rank=-1,
                                                     input=GetFilteredPageRangeRequest(
                                                         predicate=pred,
                                                         hs_type=hs_type,
                                                         account_type=account_type)
                                                     )

            if not hs_scrape_joblist:
                hs_scrape_joblist = temp_joblist
            else:
                start_job_prio = start_job_prio if start_job_prio > temp_joblist[
                    0].priority else temp_joblist[0].priority
                end_job_prio = end_job_prio if end_job_prio < temp_joblist[-1].priority else temp_joblist[-1].priority

        hs_scrape_joblist = [
            x for x in hs_scrape_joblist if start_job_prio <= x.priority <= end_job_prio]
    else:
        hs_scrape_joblist = await get_hs_page_job(req=req,
                                                  start_rank=start_rank,
                                                  end_rank=-1,
                                                  input=GetMaxHighscorePageRequest(
                                                      hs_type=hs_type, account_type=account_type)
                                                  )

    return hs_scrape_joblist, hs_scrape_joblist[-1].end_rank - hs_scrape_joblist[0].start_rank + 1, JobQueue(maxsize=N_SCRAPE_SIZE)


@finished_script
@benchmark
async def main(out_file: str, in_file: str, proxy_file: str, start_rank: int, account_type: HSAccountTypes, hs_type: HSType, hs_filter: dict[HSType, Callable[[int | float], bool]], num_workers: int):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session, proxy_list=read_proxies(proxy_file))

        hs_scrape_joblist, record_count, hs_scrape_export_q = await prepare_scrape_jobs(
            req=req,
            in_file=in_file,
            start_rank=start_rank,
            account_type=account_type,
            hs_type=hs_type,
            hs_filter=hs_filter
        )

        if hs_scrape_joblist:
            hs_scrape_job_q = JobQueue[IJob]()
            for job in hs_scrape_joblist:
                await hs_scrape_job_q.put(job)

            scrape_job_manager = JobManager(start=hs_scrape_joblist[0].page_num, end=hs_scrape_joblist[-1].page_num)
            hs_scrape_workers = create_workers(        
                    req=req,
                    in_queue=hs_scrape_job_q,
                    out_queue=hs_scrape_export_q,
                    job_manager=scrape_job_manager,
                    request_fn=request_hs_page,
                    enqueue_fn=enqueue_page_usernames,
                    num_workers=N_SCRAPE_WORKERS
                )

            filter_start = hs_scrape_joblist[0].start_rank
            filter_end = hs_scrape_joblist[0].end_rank
        else:
            hs_scrape_workers = []
            filter_start = hs_scrape_export_q.peek().priority
            filter_end = hs_scrape_export_q.last().priority

        filter_q = asyncio.Queue()
        filter_job_manager = JobManager(start=filter_start, end=filter_end)
        filter_workers = create_workers(        
                req=req,
                in_queue=hs_scrape_export_q,
                out_queue=filter_q,
                job_manager=filter_job_manager,
                request_fn=request_user_stats,
                enqueue_fn=partial(enqueue_user_stats_filter, hs_filter=hs_filter),
                num_workers=num_workers
            )


        T: list[asyncio.Task[None]] = [asyncio.create_task(
            write_records(in_queue=filter_q,
                          out_file=out_file,
                          total=record_count,
                          format=filtered_result_formatter
                          )
        )]
        for w in hs_scrape_workers:
            T.append(asyncio.create_task(
                w.run(initial_delay=0.2)
            ))
        for i, w in enumerate(filter_workers):
            T.append(asyncio.create_task(
                w.run(initial_delay=i * 0.1)
            ))
        try:
            await asyncio.gather(*T)
        finally:
            for task in T:
                task.cancel()
            await asyncio.gather(*T, return_exceptions=True)

if __name__ == '__main__':
    def parse_key_value_pairs(arg) -> dict[HSType, Callable[[int | float], bool]]:
        kv_pairs = arg.split(',')
        result = {}

        for pair in kv_pairs:
            match = re.match(r'\s*(.*?)\s*(<=|>=|=|<|>)\s*(.*?)\s*$', pair)
            if not match:
                raise ValueError(f"Invalid pair format: '{pair}'")

            key_str, op, value_str = match.groups()
            key = HSType.from_string(key_str.strip())
            value_str = value_str.strip()
            try:
                value = float(value_str)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                raise ValueError(f"Invalid number: {value_str}")

            if op == '=':
                def func(x, v=value): return x == v
            elif op == '<':
                def func(x, v=value): return x < v
            elif op == '>':
                def func(x, v=value): return x > v
            elif op == '<=':
                def func(x, v=value): return x <= v
            elif op == '>=':
                def func(x, v=value): return x >= v
            else:
                raise ValueError(f"Unsupported operator: '{op}'")

            result[key] = func

        return result

    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--in-file',
                        help="Path to the in file, reads from highscores if this argument is missing.")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--rank-start', default=1, type=int,
                        help="Rank number that it should start filtering at (default: 1)")
    parser.add_argument('--account-type', default='regular',
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should look at (default: 'regular')")
    parser.add_argument('--hs-type', default='overall',
                        type=HSType.from_string, choices=list(HSType), help="Hiscore category it should pull from")
    parser.add_argument('--filter', type=parse_key_value_pairs, required=True,
                        help="Custom filter on what the accounts should have")
    parser.add_argument('--num-workers', default=DEFAULT_WORKER_SIZE, type=int,
                        help="Number of concurrent scraping threads")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.out_file, args.in_file, args.proxy_file, args.rank_start,
                    args.account_type, args.hs_type, args.filter, args.num_workers))
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
