import argparse
import json
import re
import sys
import threading
from request.common import CategoryRecord, HSApi, HSApiCsvMapper
from request.request import Requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def process(hs_record: CategoryRecord, **args: dict) -> None:
    rank, username = hs_record.rank, hs_record.username
    out_file, req, account_type, filter = args["out_file"], args["req"], args["account_type"], args["filter"]

    player_record = retry(req.get_user_stats, name=username,
                  account_type=account_type, idx=rank)

    if player_record.lacks_requirements(filter):
        with file_lock:
            with open(out_file, "a") as f:
                f.write(json.dumps({
                    "rank": rank,
                    "record": player_record
                }) + "\n")

    logger.info(f'finished nr: {rank} - {username}')


def main(in_file: str, out_file: str, proxy_file: str | None, start_nr: int, account_type: HSApi, filter: dict[HSApiCsvMapper, int]):
    hs_records = []
    with open(in_file, "r") as f:
        for line in f:
            data = json.loads(line)
            record = CategoryRecord(**data)
            if record.rank >= start_nr:
                hs_records.append(record)

    if proxy_file is not None:
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    req = Requests(proxies)

    spawn_threads(process, hs_records, req=req,
                  account_type=account_type, out_file=out_file, filter=filter)


if __name__ == '__main__':
    def parse_key_value_pairs(arg):
        kv_pairs = arg.split(',')
        result = {}

        for pair in kv_pairs:
            match = re.match(r'\s*(.*?)\s*(<=|>=|=|<|>)\s*(.*?)\s*$', pair)
            if not match:
                raise ValueError(f"Invalid pair format: '{pair}'")

            key_str, op, value_str = match.groups()
            key = HSApiCsvMapper.from_string(key_str.strip())
            value = int(value_str.strip())

            if op == '=':
                func = lambda x, v=value: x == v
            elif op == '<':
                func = lambda x, v=value: x < v
            elif op == '>':
                func = lambda x, v=value: x > v
            elif op == '<=':
                func = lambda x, v=value: x <= v
            elif op == '>=':
                func = lambda x, v=value: x >= v
            else:
                raise ValueError(f"Unsupported operator: '{op}'")

            result[key] = func

        return result

    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True,
                        help="Path to the input file")
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--start-nr', default=1, type=int,
                        help="Key value pair index that it should start filtering at")
    parser.add_argument('--account-type', default='regular',
                        type=HSApi.from_string, choices=list(HSApi), help="Account type it should look at (default: 'regular')")
    parser.add_argument('--filter', type=parse_key_value_pairs, required=True,
                        help="Inclusive bound on what the account should have")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.proxy_file, args.start_nr,
         args.account_type, args.filter)

    logger.info("done")
    sys.exit(0)
