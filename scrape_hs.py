import argparse
import sys

from common import HSOverall, HSOverallTableMapper
from request import get_hs_page, extract_usernames


def main(out_file, acc_type, hs_type, page_nr):
    page_size = 25
    with open(out_file, "a") as f:
        while True:
            try:
                page = get_hs_page(acc_type, hs_type, page_nr)
                extracted_names = extract_usernames(page)

                finished = False
                for key, value in extracted_names.items():
                    if page_nr - 1 * page_size > key:
                        finished = True
                        break
                    f.write('%s,%s\n' % (key, value))

                if finished:
                    break

                print(f'finished page: {page_nr}')

                if len(extracted_names) < page_size:
                    break

                page_nr += 1
            except Exception as err:
                print(err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True)
    parser.add_argument('--account-type', default='regular',
                        type=HSOverall.from_string, choices=list(HSOverall))
    parser.add_argument('--hs-type', default='overall',
                        type=HSOverallTableMapper.from_string, choices=list(HSOverallTableMapper))
    parser.add_argument('--page-nr', default=1, type=int)
    args = parser.parse_args()

    main(args.out_file, args.account_type, args.hs_type, args.page_nr)

    print("done")
    sys.exit(0)
