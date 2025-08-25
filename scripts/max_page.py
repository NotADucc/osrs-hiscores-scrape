import argparse
import asyncio
import datetime
import sys

import aiohttp

from src.request.common import HSAccountTypes, HSType
from src.request.dto import (GetMaxHighscorePageRequest,
                             GetMaxHighscorePageResult)
from src.request.request import Requests
from src.util import json_wrapper
from src.util.benchmarking import benchmark
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.log import finished_script, get_logger
from src.util.retry_handler import retry

logger = get_logger()


@finished_script
@benchmark
async def main(account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)
        max_page_res = await retry(req.get_max_page, input=GetMaxHighscorePageRequest(account_type=account_type, hs_type=hs_type))

        convert = {
            "max_page": max_page_res.page_nr,
            "max_rank": max_page_res.rank_nr,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        json_output = json_wrapper.to_json(convert, indent=1)

        print(json_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account-type', default='regular', required=True,
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should scout")
    parser.add_argument('--hs-type', type=HSType.from_string, required=True,
                        choices=list(HSType), help="Highscore Category it should scout")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.account_type, args.hs_type))
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
