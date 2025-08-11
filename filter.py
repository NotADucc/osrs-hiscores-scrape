import argparse
import asyncio
import json
import re
import sys

import aiohttp
from request.common import HSAccountTypes, HSType
from request.errors import FinishedScript
from request.job import HSLookupJob, JobCounter, JobQueue, get_hs_page_job, GetMaxHighscorePageRequest
from request.request import Requests
from request.worker import Worker, enqueue_page_usernames, request_hs_page, request_stats
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.io import read_proxies, read_hs_records, write_records
from util.log import get_logger

logger = get_logger()
N_SCRAPE_WORKERS = 2
N_SCRAPE_SIZE = 100

async def main(in_file: str, out_file: str, proxy_file: str | None, start_nr: int, account_type: HSAccountTypes, hs_type: HSType, filter: dict[HSType, int], num_workers: int):
    async def enqueue_filter(queue: asyncio.Queue, job: HSLookupJob):
        if job.result.meets_requirements(filter):
            await queue.put(job)
        else : 
            await queue.put(None)
    async with aiohttp.ClientSession() as session:
        req = Requests(session=session, proxy_list=read_proxies(proxy_file))

        if in_file is None:
            start_page_nr = (start_nr - 1) // 25 + 1 
            hs_scrape_joblist = await get_hs_page_job(req=req,
                                                    start_page=start_page_nr,
                                                    end_page=-1,
                                                    input=GetMaxHighscorePageRequest(
                                                        hs_type=hs_type, account_type=account_type)
                                                    )
            hs_scrape_job_q = JobQueue()
            for job in hs_scrape_joblist:
                await hs_scrape_job_q.put(job)

            hs_scrape_export_q = JobQueue(max_size=N_SCRAPE_SIZE)

            current_page = JobCounter(value=hs_scrape_joblist[0].page_num)
            hs_scrape_workers = [Worker(in_queue=hs_scrape_job_q, out_queue=hs_scrape_export_q, job_counter=current_page)
                                for _ in range(N_SCRAPE_WORKERS)]

            filter_q = asyncio.Queue()
            current_rank = JobCounter(value=start_nr)
            filter_workers = [Worker(in_queue=hs_scrape_export_q, out_queue=filter_q, job_counter=current_rank)
                   for _ in range(num_workers)]

            T = [asyncio.create_task(
                write_records(in_queue=filter_q,
                            out_file=out_file,
                            total=hs_scrape_joblist[-1].end_rank -
                            hs_scrape_joblist[0].start_rank + 1,
                            format=lambda job: json.dumps({"rank": job.priority, "record": job.result.to_dict()}) + '\n'
                            )
            )]
            for w in hs_scrape_workers:
                T.append(asyncio.create_task(
                    w.run(req=req, request_fn=request_hs_page,
                        enqueue_fn=enqueue_page_usernames, delay=0.2)
                ))
            for i, w in enumerate(filter_workers):
                T.append(asyncio.create_task(
                    w.run(req=req, request_fn=request_stats, enqueue_fn=enqueue_filter, delay=i * 0.1)
                ))
            try:
                await asyncio.gather(*T)
            except FinishedScript:
                pass
            finally:
                for task in T:
                    task.cancel()
                await asyncio.gather(*T, return_exceptions=True)
        else :
            hs_records = read_hs_records(in_file=in_file)
    

if __name__ == '__main__':
    def parse_key_value_pairs(arg):
        kv_pairs = arg.split(',')
        result = {}

        for pair in kv_pairs:
            match = re.match(r'\s*(.*?)\s*(<=|>=|=|<|>)\s*(.*?)\s*$', pair)
            if not match:
                raise ValueError(f"Invalid pair format: '{pair}'")

            key_str, op, value_str = match.groups()
            key = HSType.from_string(key_str.strip())
            value = int(value_str.strip())

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
    parser.add_argument('--in-file', help="Path to the input file")
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--start-nr', default=1, type=int,
                        help="Key value pair index that it should start filtering at")
    parser.add_argument('--account-type', default='regular',
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should look at (default: 'regular')")
    parser.add_argument('--hs-type',
                        type=HSType.from_string, choices=list(HSType), help="Hiscore category it should pull from")
    parser.add_argument('--filter', type=parse_key_value_pairs, required=True,
                        help="Custom filter on what the accounts should have")
    parser.add_argument('--num-workers', default=50, type=int,
                        help="Number of concurrent scraping threads")
    
    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        if not args.in_file and not args.hs_type:
            parser.error('"--in-file" or "--hs-type" is missing')

        asyncio.run(main(args.in_file, args.out_file, args.proxy_file, args.start_nr, args.account_type, args.hs_type, args.filter, args.num_workers))
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    logger.info("done")
    sys.exit(0)
