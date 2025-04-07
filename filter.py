import argparse
import sys
import threading

from request.common import HSLookup
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from util.stats_handler import get_stats_api, get_combat_stats_scrape
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def process(hs_record: tuple, **args: dict) -> None:
    idx, name = hs_record
    out_file, predicate, get_stats, account_type = args["out_file"], args["predicate"], args["get_stats"], args["account_type"]
    stats = retry(get_stats, name=name, account_type=account_type, idx=idx)
    if predicate(stats):
        with file_lock:
            with open(out_file, "a") as f:
                f.write('%s,%s,%s\n' % (idx, name, stats))
    logger.info(f'finished nr: {idx} - {name}')


def is_sub_40_cmb(stats: dict):
    return stats["combat"] and stats["combat"] < 40


def is_sub_86_range(stats: dict):
    return stats["ranged"] and stats["ranged"] < 86


def main(in_file: str, out_file: str, start_nr: int, method, account_type: str, delimiter: str):
    hs_records = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(delimiter)[:2]
            idx = int(idx)
            if idx >= start_nr:
                hs_records.append((idx, name))

    get_stats = get_stats_api if method == 'api' else get_combat_stats_scrape

    spawn_threads(process, hs_records, get_stats=get_stats,
                  account_type=account_type, out_file=out_file, predicate=is_sub_86_range)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True)
    parser.add_argument('--out-file', required=True)
    parser.add_argument('--start-nr', default=1, type=int)
    parser.add_argument('--method', default='api', choices=['api', 'scrape'])
    parser.add_argument('--account-type', default='regular',
                        type=HSLookup.from_string, choices=list(HSLookup))
    parser.add_argument('--delimiter', default=',')
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.start_nr,
         args.method, str(args.account_type), args.delimiter)

    logger.info("done")
    sys.exit(0)
