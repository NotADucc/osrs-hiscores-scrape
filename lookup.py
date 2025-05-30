import argparse
import json
import sys
from request.common import HSLookup
from util.common import StatsFlag
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.stats_handler import get_stats_api, get_combat_stats_scrape
from util.log import get_logger

logger = get_logger()


def main(name, account_type, method):
    get_stats = get_stats_api if method == 'api' else get_combat_stats_scrape

    flags = StatsFlag.default.__add__(
        StatsFlag.add_misc).__add__(StatsFlag.add_skills)

    stats = retry(get_stats, name=name, account_type=account_type, flags=flags)

    stats = json.dumps(stats)
    json_object = json.loads(stats)
    json_formatted_str = json.dumps(json_object, indent=1)

    print(json_formatted_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True,
                        help="Name that you want info about.")
    parser.add_argument('--account-type', default='regular',
                        type=HSLookup.from_string, choices=list(HSLookup), help="Account type it should look at (default: 'regular')")
    parser.add_argument('--method', default='api', choices=[
                        'api', 'scrape'], help="Either use osrs api or scrape from website")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.name, args.account_type, args.method)

    logger.info("done")
    sys.exit(0)
