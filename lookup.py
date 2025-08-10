import argparse
import asyncio
import json
import sys

import aiohttp
from request.common import HSAccountTypes
from request.dto import GetPlayerRequest
from request.errors import NotFound
from request.request import Requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.log import get_logger

logger = get_logger()


async def main(name: str, account_type: HSAccountTypes):

    async with aiohttp.ClientSession() as session:
        try:
            req = Requests(session=session)
            player_record = await retry(req.get_user_stats, input=GetPlayerRequest(username=name, account_type=account_type))
        except NotFound:
            sys.exit(0)

    json_object = json.loads(str(player_record))
    json_formatted_str = json.dumps(json_object, indent=1)

    print(json_formatted_str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True,
                        help="Name that you want info about.")
    parser.add_argument('--account-type', default='regular',
                        type=HSAccountTypes.from_string, choices=list(HSAccountTypes), help="Account type it should look at (default: 'regular')")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    try:
        asyncio.run(main(args.name, args.account_type))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Caught Error: {e}")
        sys.exit(2)

    logger.info("done")
    sys.exit(0)
