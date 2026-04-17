import argparse
import asyncio
import sys

import aiohttp

from osrs_hiscore_scrape.exception.records import NotFound
from osrs_hiscore_scrape.request.dto import GetPlayerRequest
from osrs_hiscore_scrape.request.hs_types import HSAccountTypes, HSType
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util import json_wrapper
from osrs_hiscore_scrape.log.decorators import profile_execution, log_lifecycle
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.util.retry_handler import retry
from osrs_hiscore_scrape.util.script_utils import (argparse_wrapper,
                                                   script_running_in_cmd_guard)

logger = get_logger(__name__)


def inline_dict(d):
    return "{ " + ", ".join(f'"{k}": {v}' for k, v in d.items()) + " }"


def format_section(section):
    lines = []
    for name, data in section.items():
        inline = inline_dict(data)
        lines.append(f'  "{name}": {inline}')
    return "{\n" + ",\n".join(lines) + "\n }"


@log_lifecycle
@profile_execution
async def main(name: str, account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)
        player_record = await retry(req.get_user_stats, player_req=GetPlayerRequest(username=name, account_type=account_type))

        convert = player_record.to_dict() if not hs_type else \
            {
            "rank": player_record.overall.rank,
            "username": player_record.username,
            "timestamp": player_record.ts.isoformat(),
            hs_type.name: player_record.get_stat(hs_type=hs_type),
        }

        convert_copy = convert.copy()

        convert_copy["skills"] = "__SKILLS__"
        convert_copy["misc"] = "__MISC__"
        json_output = json_wrapper.to_json(convert_copy, indent=1)

        json_output = json_output.replace(
            '"__SKILLS__"', format_section(convert["skills"]))
        json_output = json_output.replace(
            '"__MISC__"', format_section(convert["misc"]))

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
