import ast
import sys
import argparse

from util.common import calc_cmb
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.log import get_logger

logger = get_logger()


def main(in_main, in_merge, out_file, delimiter):
    dct = {}

    with open(in_main, "r") as f:
        for line in f:
            idx, name, stats = line.strip().split(delimiter, 2)
            dct[idx] = (name, ast.literal_eval(stats))

    with open(in_merge, "r") as f:
        for line in f:
            idx, name, stats = line.strip().split(delimiter, 2)
            if idx not in dct:
                dct[idx] = (name, ast.literal_eval(stats))
            else:
                dct_stats = dct[idx][1]
                stats = ast.literal_eval(stats)
                att = max(int(stats["attack"]), int(dct_stats["attack"]))
                de = max(int(stats["defence"]), int(dct_stats["defence"]))
                st = max(int(stats["strength"]), int(dct_stats["strength"]))
                hp = max(int(stats["hitpoints"]), int(dct_stats["hitpoints"]))
                ra = max(int(stats["ranged"]), int(dct_stats["ranged"]))
                pr = max(int(stats["prayer"]), int(dct_stats["prayer"]))
                ma = max(int(stats["magic"]), int(dct_stats["magic"]))
                zuk = max(int(stats["zuk-kc"]), int(dct_stats["zuk-kc"]))
                cmb = calc_cmb(att, de, st, hp, ra, pr, ma)
                stats = {
                    'combat': cmb,
                    'attack': att,
                    'defence': de,
                    'strength': st,
                    'hitpoints': hp,
                    'ranged': ra,
                    'prayer': pr,
                    'magic': ma,
                    'zuk-kc': zuk
                }
                dct[idx] = (name, stats)

    with open(out_file, "w") as file:
        for k, v in dct.items():
            file.write(f'{k},{v[0]},{v[1]}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-main', required=True,
                        help="Path to the main input file")
    parser.add_argument('--in-merge', required=True,
                        help="Path to the file to merge in")
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--delimiter', default=',',
                        help="Delimiter used in the files (default: ,)")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.in_main, args.in_merge, args.out_file, args.delimiter)

    logger.info("done")
    sys.exit(0)
