import argparse
import asyncio
import sys

import aiohttp

from src.request.common import HSAccountTypes, HSType
from src.request.dto import GetPlayerRequest
from src.request.errors import NotFound
from src.request.request import Requests
from src.util import json_wrapper
from src.util.benchmarking import benchmark
from src.util.log import get_logger, log_execution
from src.util.retry_handler import retry
from src.util.script_utils import argparse_wrapper, script_running_in_cmd_guard

logger = get_logger()


@log_execution
@benchmark
async def main(name: str, account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)
        player_record = await retry(req.get_user_stats, player_req=GetPlayerRequest(username=name, account_type=account_type))

        convert = player_record.to_dict() if not hs_type else \
            {
                "rank": player_record.rank,
                "username": player_record.username,
                "timestamp": player_record.ts.isoformat(),
                hs_type.name: player_record.get_stat(hs_type=hs_type),
        }
        json_output = json_wrapper.to_json(convert, indent=1)

        print(json_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True,
                        help="Name that you want info about.")
    parser.add_argument('--account-type', default='regular',
                        type=argparse_wrapper(HSAccountTypes.from_string),
                        choices=list(HSAccountTypes), help="Account type it should look at (default: 'regular')")
    parser.add_argument('--hs-type', type=argparse_wrapper(HSType.from_string),
                        choices=list(HSType), help="Filter on specific hiscore category")

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.name, args.account_type, args.hs_type))
    except NotFound:
        sys.exit(0)
    except Exception as e:
        logger.error(str(e))
        sys.exit(2)
