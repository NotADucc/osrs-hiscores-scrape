import argparse
import sys

from request.common import HSLookup
from request.request import lookup
from util.retry_handler import retry
from util.combat_lvl_handler import get_combat_lvl_api, get_combat_lvl_scrape


def main(in_file, out_file, hs_nr, method, acc_type):
    names = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(",", 1)
            names.append((idx, name))

    hs_idx = hs_nr - 1
    if hs_idx < 0 or hs_idx > len(names):
        return

    get_combat_lvl = get_combat_lvl_api if method == 'api' else get_combat_lvl_scrape
    for index, (idx, name) in enumerate(names[hs_idx:], start=hs_idx):
        cmb_lvl = retry(get_combat_lvl, idx, name, acc_type)
        if cmb_lvl and cmb_lvl < 40:
            with open(out_file, "a") as ff:
                ff.write('%s,%s,%s\n' % (idx, name, cmb_lvl))
        print(f'finished nr: {idx} - {name}')


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
