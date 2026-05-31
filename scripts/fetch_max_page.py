import argparse
import asyncio
import datetime
import sys

import aiohttp

from osrs_hiscore_scrape.cli.helpers import script_running_in_cmd_guard
from osrs_hiscore_scrape.cli.presets import OSRSArgumentParser
from osrs_hiscore_scrape.log.decorators import log_lifecycle, profile_execution
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.request.dto import GetMaxHighscorePageRequest
from osrs_hiscore_scrape.request.hs_account_types import HSAccountTypes
from osrs_hiscore_scrape.request.hs_types import HSType
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util import json_wrapper
from osrs_hiscore_scrape.util.retry_handler import retry

logger = get_logger(__name__)


@log_lifecycle
@profile_execution
async def main(account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        max_page_res = await retry(req.get_max_page, max_page_req=GetMaxHighscorePageRequest(account_type=account_type, hs_type=hs_type))

        convert = {
            "account_type": account_type.name,
            "category": hs_type.name,
            "max_page": max_page_res.page_nr,
            "max_rank": max_page_res.rank_nr,
            "timestamp": timestamp,
        }
        json_output = json_wrapper.to_json(convert, indent=1)

        print(json_output)


if __name__ == '__main__':
    parser = OSRSArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.account_type(required=True, default=None) \
        .hs_type(required=True, default=None)

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.account_type, args.hs_type))
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
