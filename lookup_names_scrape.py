import argparse
import sys

from time import sleep
from common import HSCSVMapper, HSLookup, calc_cmb
from request import lookup_scrape, extract_stats

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
            retries, max_retries = 0, 3
            while retries < max_retries:
                try:
                    extracted_stats = extract_stats
                   
                    att = extracted_stats.get('Attack', 1)
                    de = extracted_stats.get('Defence', 1)
                    st = extracted_stats.get('Strength', 1)
                    hp = extracted_stats.get('Hitpoints', 10)
                    ra = extracted_stats.get('Ranged', 1)
                    pr = extracted_stats.get('Prayer', 1)
                    ma = extracted_stats.get('Magic', 1)

                    cmb_lvl = calc_cmb(att, de, st, hp, ra, pr, ma)
                    if cmb_lvl < 40:
                        ff.write('%s:%s cmb %s\n' % (index + 1, val, cmb_lvl))

                    print(f'finished nr: {index + 1} - {val}')
                    break 
                except Exception as err:
                    print(err)
                    print(f"Error occurred at index {index}: {type(err)}. Retrying...")
                    retries += 1
                    sleep(10)
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