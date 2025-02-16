import argparse
import sys

from common import HSOverall, HSOverallTableMapper
from request import get_hs_page, extract_usernames

def main(out_file, page_nr):
    names = {}
    with open(out_file, "a") as f:
        while True :
            page = get_hs_page(HSOverall.pure, HSOverallTableMapper.zuk, page_nr)
            extracted_names = extract_usernames(page)
            name_cnt = len(names)
            names.update(extracted_names)
            if (name_cnt == len(names)) :
                break
  
            for key, value in extracted_names.items():  
                f.write('%s,%s\n' % (key, value))
            print(f'finished page: {page_nr}')
            page_nr += 1
            
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape data from the OSRS hiscores.")
    parser.add_argument('--out-file', required=True, help="dump scraped data to this CSV file in append mode")
    parser.add_argument('--page_nr', default=1, type=int, help="start page nr")
    args = parser.parse_args()

    main(args.out_file, args.page_nr)
    
    print("done")
    sys.exit(0)