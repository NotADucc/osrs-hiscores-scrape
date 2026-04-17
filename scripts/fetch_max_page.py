import argparse
import asyncio
import datetime
import sys

import aiohttp

from osrs_hiscore_scrape.request.dto import GetMaxHighscorePageRequest
from osrs_hiscore_scrape.request.hs_types import HSAccountTypes, HSType
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util import json_wrapper
from osrs_hiscore_scrape.log.decorators import log_lifecycle, profile_execution
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.util.retry_handler import retry
from osrs_hiscore_scrape.util.script_utils import (argparse_wrapper,
                                                   script_running_in_cmd_guard)

logger = get_logger(__name__)


@log_lifecycle
@profile_execution
async def main(account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        max_page_res = await retry(req.get_max_page, max_page_req=GetMaxHighscorePageRequest(account_type=account_type, hs_type=hs_type))

        convert = {
            "max_page": max_page_res.page_nr,
            "max_rank": max_page_res.rank_nr,
            "timestamp": timestamp,
        }
        json_output = json_wrapper.to_json(convert, indent=1)

        print(json_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account-type', required=True,
                        type=argparse_wrapper(HSAccountTypes.from_string),
                        choices=list(HSAccountTypes), help="Account type it should scout")
    parser.add_argument('--hs-type', type=argparse_wrapper(HSType.from_string), required=True,
                        choices=list(HSType), help="Highscore Category it should scout")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.account_type, args.hs_type))
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
