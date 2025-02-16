import argparse
import sys

from common import HSType, HSTableMapper
from request import get_hs_page, extract_usernames

def main(out_file, page_nr):
    names = {}
    
    while True :
        page = get_hs_page(HSType.pure, HSTableMapper.zuk, page_nr)
        extracted_names = extract_usernames(page)
        name_cnt = len(names)
        names.update(extracted_names)
        if (name_cnt == len(names)) :
            break
        page_nr += 1
    
    with open(out_file, "a") as f:
        for key, value in names.items():  
            f.write('%s:%s\n' % (key, value))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape data from the OSRS hiscores.")
    parser.add_argument('--out-file', required=True, help="dump scraped data to this CSV file in append mode")
    parser.add_argument('--page_nr', default=1, type=int, help="number of concurrent scraping threads")
    args = parser.parse_args()

    main(args.out_file, args.page_nr)
    
    print("done")
    sys.exit(0)