import argparse
import asyncio
import sys

import aiohttp

from src.request.common import HSAccountTypes
from src.request.dto import GetPlayerRequest
from src.request.errors import NotFound
from src.request.request import Requests
from src.util import json_wrapper
from src.util.benchmarking import benchmark
from src.util.guard_clause_handler import script_running_in_cmd_guard
from src.util.log import finished_script, get_logger
from src.util.retry_handler import retry

logger = get_logger()


@finished_script
@benchmark
async def main(name: str, account_type: HSAccountTypes):

    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)
        player_record = await retry(req.get_user_stats, input=GetPlayerRequest(username=name, account_type=account_type))
        json_object = json_wrapper.from_json(str(player_record))
        json_formatted_str = json_wrapper.to_json(json_object, indent=1)

        print(json_formatted_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True,
                        help="Name that you want info about.")
    parser.add_argument('--account-type', default='regular',
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should look at (default: 'regular')")

    script_running_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.name, args.account_type))
    except NotFound:
        sys.exit(0)
    except Exception as e:
        logger.error(e)
        sys.exit(2)
