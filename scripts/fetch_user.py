import argparse
import asyncio
import sys

import aiohttp

from osrs_hiscore_scrape.exception.records import NotFound
from osrs_hiscore_scrape.log.decorators import log_lifecycle, profile_execution
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.request.dto import GetPlayerRequest
from osrs_hiscore_scrape.request.hs_types import HSAccountTypes, HSType
from osrs_hiscore_scrape.request.records import PlayerRecord
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util import json_wrapper
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
async def main(name: str, lookup_account_type: HSAccountTypes, hs_type: HSType):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)

        base_routines = {
            lookup_account_type: retry(req.get_user_stats, player_req=GetPlayerRequest(username=name, account_type=lookup_account_type)),
        }

        if lookup_account_type == HSAccountTypes.regular:
            base_routines[HSAccountTypes.im] = retry(req.get_user_stats, player_req=GetPlayerRequest(
                username=name, account_type=HSAccountTypes.im), suppress_logger=True)

        temp_results = await asyncio.gather(*base_routines.values(), return_exceptions=True)
        results = dict(zip(base_routines.keys(), temp_results))

        player_record = results[lookup_account_type]
        if isinstance(player_record, NotFound):
            raise player_record

        im_result = results.get(HSAccountTypes.im, None)
        has_iron_result = isinstance(im_result, PlayerRecord)

        if has_iron_result:
            extra_iron_routines = {
                HSAccountTypes.uim: retry(req.get_user_stats, player_req=GetPlayerRequest(username=name, account_type=HSAccountTypes.uim), suppress_logger=True),
                HSAccountTypes.hc: retry(req.get_user_stats, player_req=GetPlayerRequest(
                    username=name, account_type=HSAccountTypes.hc), suppress_logger=True)
            }
            temp_results = await asyncio.gather(*extra_iron_routines.values(), return_exceptions=True)
            results.update(dict(zip(extra_iron_routines.keys(), temp_results)))

        # it's needed for linter even though we do notfound check
        assert isinstance(player_record, PlayerRecord)

        predicted_account_type = HSAccountTypes.regular
        downgraded_statuses = {
            "de_ironed": {
                "account_type": None,  # skip in loop
                "value": None,
            },
            "de_ulted": {
                "account_type": HSAccountTypes.uim,
                "value": None,
            },
            "dead_hc": {
                "account_type": HSAccountTypes.hc,
                "value": None,
            },
        }

        if has_iron_result:
            im_overall = im_result.get_stat(HSType.overall)
            main_overall = player_record.get_stat(HSType.overall)

            downgraded_statuses["de_ironed"]["value"] = im_overall < main_overall

            if not downgraded_statuses["de_ironed"]["value"]:
                predicted_account_type = HSAccountTypes.im

            for _, info in downgraded_statuses.items():
                account_type = info["account_type"]
                if account_type is None:
                    continue

                r = results.get(account_type, None)
                if isinstance(r, PlayerRecord):
                    info["value"] = r.get_stat(HSType.overall) < main_overall
                    if not info["value"]:
                        predicted_account_type = account_type

        base = player_record.to_dict() if not hs_type else \
            {
            "username": player_record.username,
            "timestamp": player_record.ts.isoformat(),
            hs_type.name: player_record.get_stat(hs_type=hs_type),
        }

        convert = {}

        for k, v in base.items():
            convert[k] = v

            if k == "username":
                convert["account_type"] = predicted_account_type.name

                for k, v in downgraded_statuses.items():
                    if v["value"] is not None:
                        convert[k] = v["value"]

        convert_copy = convert.copy()

        sections = ["skills", "seasonal_modes",
                    "misc", "minigames", "clues", "bosses"]
        for section in sections:
            convert_copy[section] = f'__{section}__'

        json_output = json_wrapper.to_json(convert_copy, indent=1)

        for section in sections:
            json_output = json_output.replace(
                f'"__{section}__"', format_section(convert[section]))

        colored_text = [
            f"\x1b[31;20m{line}\x1b[0m" if '"score": 0' in line or '"xp": 0' in line
            else line
            for line in json_output.splitlines()
        ]

        print("\n".join(colored_text))


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
        logger.error(str(e), exc_info=True)
        sys.exit(2)
