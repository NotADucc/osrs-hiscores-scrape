import argparse
import json
import sys
from request.common import HSApi
from request.request import Requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.log import get_logger

logger = get_logger()


def main(name: str, account_type: HSApi):
    req = Requests()

    player_record = retry(req.get_user_stats, name=name,
                          account_type=account_type)

    if not player_record:
        return None

    json_object = json.loads(str(player_record))
    json_formatted_str = json.dumps(json_object, indent=1)

    print(json_formatted_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True,
                        help="Name that you want info about.")
    parser.add_argument('--account-type', default='regular',
                        type=HSApi.from_string, choices=list(HSApi), help="Account type it should look at (default: 'regular')")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.name, args.account_type)

    logger.info("done")
    sys.exit(0)
