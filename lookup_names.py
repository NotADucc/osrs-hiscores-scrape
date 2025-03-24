import argparse
import sys
import concurrent.futures
import threading
import functools

from request.common import HSLookup
from util.retry_handler import retry
from util.combat_lvl_handler import get_combat_lvl_api, get_combat_lvl_scrape

file_lock = threading.Lock()


def main(in_file, out_file, start_nr, method, acc_type):
    hs_records = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(",", 1)
            idx = int(idx)
            if idx >= start_nr:
                hs_records.append((idx, name))

    get_combat_lvl = get_combat_lvl_api if method == 'api' else get_combat_lvl_scrape

    def process(hs_record, get_combat_lvl, acc_type, out_file):
        idx, name = hs_record
        cmb_lvl = retry(get_combat_lvl, idx, name, acc_type)
        if cmb_lvl and cmb_lvl < 40:
            with file_lock:
                with open(out_file, "a") as ff:
                    ff.write('%s,%s,%s\n' % (idx, name, cmb_lvl))
        print(f'finished nr: {idx} - {name}')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        process_with_args = functools.partial(
            process, get_combat_lvl=get_combat_lvl, acc_type=acc_type, out_file=out_file)
        executor.map(process_with_args, hs_records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True)
    parser.add_argument('--out-file', required=True)
    parser.add_argument('--start-nr', default=1, type=int)
    parser.add_argument('--method', default='api', choices=['api', 'scrape'])
    parser.add_argument('--account-type', default='regular',
                        type=HSLookup.from_string, choices=list(HSLookup))
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.start_nr,
         args.method, str(args.account_type))

    print("done")
    sys.exit(0)
