import argparse
import sys

from common import HSApiCsvMapper, calc_cmb
from request import lookup
from run import retry

def main(in_file, out_file, hs_nr, method):
    names = []
    with open(in_file, "r") as f:
        for line in f:
            idx, name = line.strip().split(",", 1)
            names.append((idx, name))
            
    hs_idx = hs_nr - 1     
    if hs_idx < 0 or hs_idx > len(names) :
        return
        
    transform_user = transform_user_api if method == 'api' else transform_user_scrape
    for index, (idx, name) in enumerate(names[hs_idx:], start=hs_idx):
        cmb_lvl = retry(transform_user, idx, name)
        if cmb_lvl and cmb_lvl < 40:
            with open(out_file, "a") as ff:
                ff.write('%s,%s,%s\n' % (idx, name, cmb_lvl))
        print(f'finished nr: {idx} - {name}')
        
def transform_user_api(_, name) :
    csv = lookup(name).split(b'\n')
    att = int(csv[HSApiCsvMapper.attack.value].split(b',')[1])
    de = int(csv[HSApiCsvMapper.defence.value].split(b',')[1])
    st = int(csv[HSApiCsvMapper.strength.value].split(b',')[1])
    hp = int(csv[HSApiCsvMapper.hitpoints.value].split(b',')[1])
    ra = int(csv[HSApiCsvMapper.ranged.value].split(b',')[1])
    pr = int(csv[HSApiCsvMapper.prayer.value].split(b',')[1])
    ma = int(csv[HSApiCsvMapper.magic.value].split(b',')[1])
    return calc_cmb(att, de, st, hp, ra, pr, ma)
    
def transform_user_scrape(_, name) :
    page = lookup_scrape(name, HSLookup.pure)
    extracted_stats = extract_stats(page)
    
    if extracted_stats.get('TzKal-Zuk', 0) == 0 :
        return None
        
    att = extracted_stats.get('Attack', {'lvl': 1})['lvl']
    de = extracted_stats.get('Defence', {'lvl': 1})['lvl']
    st = extracted_stats.get('Strength', {'lvl': 1})['lvl']
    hp = extracted_stats.get('Hitpoints', {'lvl': 10})['lvl']
    ra = extracted_stats.get('Ranged', {'lvl': 1})['lvl']
    pr = extracted_stats.get('Prayer', {'lvl': 1})['lvl']
    ma = extracted_stats.get('Magic', {'lvl': 1})['lvl']
    return calc_cmb(att, de, st, hp, ra, pr, ma)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', required=True)
    parser.add_argument('--out-file', required=True)
    parser.add_argument('--start-nr', default=1, type=int)
    parser.add_argument('--method', default='api', choices=['api', 'scrape'])
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.start_hs_nr, args.method)
    
    print("done")
    sys.exit(0)