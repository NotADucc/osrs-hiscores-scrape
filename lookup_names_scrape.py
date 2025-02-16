import argparse
import sys

from time import sleep
from common import HSLookup, calc_cmb
from request import lookup_scrape, extract_stats
from run import retry

def main(in_file, out_file, hs_nr):
    names = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(",", 1)
            names.append((idx, name))
            
    hs_idx = hs_nr - 1     
    if hs_idx < 0 or hs_idx > len(names) :
        return
        
    for index, (idx, name) in enumerate(names[hs_idx:], start=hs_idx):
        retry(transform_user, name, idx, out_file)
         
         
def transform_user(name, idx, out_file) :
    page = lookup_scrape(name, HSLookup.pure)
    extracted_stats = extract_stats(page)
    
    if extracted_stats.get('TzKal-Zuk', 0) == 0 :
        print(f'finished nr: {idx} - {name}')
        return
        
    att = extracted_stats.get('Attack', {'lvl': 1})['lvl']
    de = extracted_stats.get('Defence', {'lvl': 1})['lvl']
    st = extracted_stats.get('Strength', {'lvl': 1})['lvl']
    hp = extracted_stats.get('Hitpoints', {'lvl': 10})['lvl']
    ra = extracted_stats.get('Ranged', {'lvl': 1})['lvl']
    pr = extracted_stats.get('Prayer', {'lvl': 1})['lvl']
    ma = extracted_stats.get('Magic', {'lvl': 1})['lvl']
    
    cmb_lvl = calc_cmb(att, de, st, hp, ra, pr, ma)
    if cmb_lvl < 40:
        with open(out_file, "a") as ff:
            ff.write('%s,%s,%s\n' % (idx, name, cmb_lvl))

    print(f'finished nr: {idx} - {name}')
       
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape data from the OSRS hiscores.")
    parser.add_argument('--in-file', required=True, help="read names to lookup")
    parser.add_argument('--out-file', required=True, help="write result")
    parser.add_argument('--start_hs_nr', default=1, type=int, help="start hs nr")
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.start_hs_nr)
    
    print("done")
    sys.exit(0)