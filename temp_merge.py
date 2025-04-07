import ast
import sys
from util.common import calc_cmb
from util.log import get_logger

logger = get_logger()


def main():
    regular, pure = '[entire_pure_set] regular_sub_86_range_inf.txt', '[entire_pure_set] pure_sub_86_range_inf.txt'
    output = '[cleaned_up] sub_86_range_inf.txt'
    dct = {}

    with open(regular, "r") as f:
        for line in f:
            idx, name, stats = line.strip().split(",", 2)
            dct[idx] = (name, ast.literal_eval(stats))

    with open(pure, "r") as f:
        for line in f:
            idx, name, stats = line.strip().split(",", 2)
            if idx not in dct :
                dct[idx] = (name, ast.literal_eval(stats))
            else :
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
                
    with open(output, "w") as file:
        for k, v in dct.items():
            file.write(f'{k},{v[0]},{v[1]}\n')

if __name__ == '__main__':
    main()
    logger.info("done")
    sys.exit(0)
