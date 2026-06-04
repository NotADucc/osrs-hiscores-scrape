import argparse
import asyncio
import sys

import aiohttp

from osrs_hiscore_scrape.cli.helpers import script_running_in_cmd_guard
from osrs_hiscore_scrape.cli.presets import OSRSArgumentParser
from osrs_hiscore_scrape.exception.records import NotFound
from osrs_hiscore_scrape.log.decorators import log_lifecycle, profile_execution
from osrs_hiscore_scrape.log.logger import get_logger
from osrs_hiscore_scrape.request.dto import GetPlayerRequest
from osrs_hiscore_scrape.request.hs_account_types import HSAccountTypes
from osrs_hiscore_scrape.request.hs_types import HSType
from osrs_hiscore_scrape.request.records import PlayerRecord
from osrs_hiscore_scrape.request.request import Requests
from osrs_hiscore_scrape.util import json_wrapper
from osrs_hiscore_scrape.util.retry_handler import retry

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
async def main(username: str, lookup_account_type: HSAccountTypes, hs_type: HSType | None):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        req = Requests(session=session)
        main_game_lookup = lookup_account_type not in (HSAccountTypes.dmm, HSAccountTypes.leagues, HSAccountTypes.tournament, HSAccountTypes.fsw)

        if main_game_lookup:
            predicted_account_type = [HSAccountTypes.main]
            base_routines = {
                HSAccountTypes.main: lambda: retry(req.get_user_stats, player_req=GetPlayerRequest(username=username, account_type=HSAccountTypes.main), suppress_logger=True),
                HSAccountTypes.im: lambda: retry(req.get_user_stats, player_req=GetPlayerRequest(username=username, account_type=HSAccountTypes.im), suppress_logger=True),
            }
        else:
            predicted_account_type = [lookup_account_type]
            base_routines = {}

        base_routines[lookup_account_type] = lambda: retry(
            req.get_user_stats, player_req=GetPlayerRequest(username=username, account_type=lookup_account_type))

        temp_results = await asyncio.gather(*(fn() for fn in base_routines.values()), return_exceptions=True)
        results = dict(zip(base_routines.keys(), temp_results))

        player_record = results[lookup_account_type]
        if isinstance(player_record, NotFound):
            raise player_record

        im_result = results.get(HSAccountTypes.im, None)
        has_iron_result = isinstance(im_result, PlayerRecord)

        if has_iron_result and lookup_account_type in (HSAccountTypes.main, HSAccountTypes.im, HSAccountTypes.skiller, HSAccountTypes.pure):
            extra_iron_routines = {
                HSAccountTypes.uim: retry(req.get_user_stats, player_req=GetPlayerRequest(username=username, account_type=HSAccountTypes.uim), suppress_logger=True),
                HSAccountTypes.hc: retry(req.get_user_stats, player_req=GetPlayerRequest(
                    username=username, account_type=HSAccountTypes.hc), suppress_logger=True)
            }
            temp_results = await asyncio.gather(*extra_iron_routines.values(), return_exceptions=True)
            results.update(dict(zip(extra_iron_routines.keys(), temp_results)))

        # it's needed for linter even though we do notfound check
        assert isinstance(player_record, PlayerRecord)

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
            "ruined_pure": {
                "account_type": HSAccountTypes.pure,
                "value": None,
            },
            "ruined_skiller": {
                "account_type": HSAccountTypes.skiller,
                "value": None,
            },
        }

        if main_game_lookup:
            main_result = results.get(HSAccountTypes.main, None)
            assert isinstance(main_result, PlayerRecord)

            main_overall = main_result.get_stat(HSType.overall)

            if has_iron_result:
                im_overall = im_result.get_stat(HSType.overall)
                downgraded_statuses["de_ironed"]["value"] = im_overall < main_overall

                if not downgraded_statuses["de_ironed"]["value"]:
                    predicted_account_type.append(HSAccountTypes.im)

            for _, info in downgraded_statuses.items():
                account_type = info["account_type"]
                if account_type is None:
                    continue

                r = results.get(account_type, None)
                if isinstance(r, PlayerRecord):
                    info["value"] = r.get_stat(HSType.overall) < main_overall
                    if not info["value"]:
                        predicted_account_type.append(account_type)

        if any(t in predicted_account_type for t in (HSAccountTypes.im, HSAccountTypes.pure, HSAccountTypes.skiller)):
            if HSAccountTypes.main in predicted_account_type:
                predicted_account_type.remove(HSAccountTypes.main)

        if any(t in predicted_account_type for t in (HSAccountTypes.uim, HSAccountTypes.hc)):
            if HSAccountTypes.im in predicted_account_type:
                predicted_account_type.remove(HSAccountTypes.im)

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
                convert["source_account_type"] = lookup_account_type.name
                convert["predicted_account_type"] = [item.name for item in predicted_account_type]

                for k, v in downgraded_statuses.items():
                    if v["value"] is not None:
                        convert[k] = v["value"]

        convert_copy = convert.copy()

        sections = ["skills", "seasonal_modes",
                    "misc", "minigames", "clues", "bosses"]
        for section in sections:
            if section in convert_copy:
                convert_copy[section] = f'__{section}__'

        convert_copy["predicted_account_type"] = "__PREDICTED__"

        json_output = json_wrapper.to_json(convert_copy, indent=1)

        for section in sections:
            if section in convert:
                json_output = json_output.replace(
                    f'"__{section}__"', format_section(convert[section]))

        json_output = json_output.replace(
            '"__PREDICTED__"',
            json_wrapper.to_json(convert["predicted_account_type"])
        )

        HIGHLIGHT_PATTERNS = (
            '"score": 0',
            '"score": -1',
            '"xp": 0',
        )

        colored_text = [
            f"\x1b[31;20m{line}\x1b[0m" if any(pattern in line for pattern in HIGHLIGHT_PATTERNS)
            else line
            for line in json_output.splitlines()
        ]

        print("\n".join(colored_text))
        return convert


if __name__ == '__main__':
    parser = OSRSArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.username(required=True) \
        .account_type() \
        .hs_type(default=None)

    script_running_in_cmd_guard()
    args = parser.parse_args()

    try:
        asyncio.run(main(args.username, args.account_type, args.hs_type))
    except NotFound:
        sys.exit(0)
    except Exception as e:
        logger.error(str(e), exc_info=True)
        sys.exit(2)
