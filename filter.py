import argparse
import sys
import threading
from request.common import HSApi, HSApiCsvMapper
from request.request import Requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def process(hs_record: tuple, **args: dict) -> None:
    idx, name = hs_record
    out_file, req, account_type, filter = args["out_file"], args["req"], args["account_type"], args["filter"]

    stats = retry(req.get_user_stats, name=name,
                  account_type=account_type, idx=idx)

    if all(stats.get(filter_stat.name, 0) <= filter_val for filter_stat, filter_val in filter.items()):
        with file_lock:
            with open(out_file, "a") as f:
                f.write('%s,%s,%s\n' % (idx, name, stats))

    logger.info(f'finished nr: {idx} - {name}')


def main(in_file: str, out_file: str, proxy_file: str | None, start_nr: int, account_type: HSApi, delimiter: str, filter: dict):
    hs_records = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(delimiter)[:2]
            idx = int(idx)
            if idx >= start_nr:
                hs_records.append((idx, name))

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
        return {HSApiCsvMapper.from_string(k.strip()): int(v.strip()) for k, v in (pair.split(':') for pair in kv_pairs)}

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
    parser.add_argument('--delimiter', default=',',
                        help="Delimiter used in the files (default: ,)")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.proxy_file, args.start_nr,
         args.account_type, args.delimiter, args.filter)

    logger.info("done")
    sys.exit(0)
