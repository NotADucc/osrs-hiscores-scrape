import argparse
import sys

from time import sleep
from common import HSCSVMapper, calc_cmb
from request import lookup

def main(in_file, out_file, hs_nr):
    names = []
    with open(in_file, "r") as f:
        for line in f:
            _, value = line.strip().split(":", 1)
            names.append(value)
            
    hs_idx = hs_nr - 1     
    if hs_idx < 0 or hs_idx > len(names) :
        return

    with open(out_file, "a") as ff:
        for index, val in enumerate(names[hs_idx:], start=hs_idx):
            retries, max_retries = 0, 5
            while retries < max_retries:
                try:
                    csv = lookup(val).split(b'\n')
                    att = int(csv[HSCSVMapper.attack.value].split(b',')[1])
                    de = int(csv[HSCSVMapper.defence.value].split(b',')[1])
                    st = int(csv[HSCSVMapper.strength.value].split(b',')[1])
                    hp = int(csv[HSCSVMapper.hitpoints.value].split(b',')[1])
                    ra = int(csv[HSCSVMapper.ranged.value].split(b',')[1])
                    pr = int(csv[HSCSVMapper.prayer.value].split(b',')[1])
                    ma = int(csv[HSCSVMapper.magic.value].split(b',')[1])

                    cmb_lvl = calc_cmb(att, de, st, hp, ra, pr, ma)
                    if cmb_lvl < 40:
                        ff.write('%s:%s cmb %s\n' % (index + 1, val, cmb_lvl))

                    print(f'finished nr: {index + 1} - {val}')
                    break 
                except Exception as err:
                    print(err)
                    print(f"Error occurred at index {index}: {type(err)}. Retrying...")
                    retries += 1
                    sleep(30 * retries)
                    if retries == max_retries:
                        with open(out_file + '.err', "a") as fff:
                            fff.write('COULD NOT FIND %s:%s\n' % (index + 1, val))
                        print('max retries reached')
                        break
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape data from the OSRS hiscores.")
    parser.add_argument('--in-file', required=True, help="read names to lookup")
    parser.add_argument('--out-file', required=True, help="write result")
    parser.add_argument('--start_hs_nr', default=1, type=int, help="start hs nr")
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.start_hs_nr)
    
    print("done")
    sys.exit(0)