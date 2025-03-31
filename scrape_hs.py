import argparse
import sys
import threading
import logging

from util.retry_handler import retry
from util.threading_handler import spawn_threads
from request.common import HSOverall, HSOverallTableMapper
from request.request import get_hs_page, extract_highscore_records

file_lock = threading.Lock()


def process(page_nr, **args):
    acc_type = args["acc_type"]
    hs_type = args["hs_type"]
    out_file = args["out_file"]
    try:
        page = retry(get_hs_page, acc_type, hs_type, page_nr)
        extracted_records = extract_highscore_records(page)

        with file_lock:
            with open(out_file, "a") as f:
                for key, value in extracted_records.items():
                    f.write('%s,%s\n' % (key, value))

        logging.info(f'finished page: {page_nr}')
    except Exception as err:
        print(err)


def main(out_file, acc_type, hs_type, page_nr, page_size=25):
    max_page = find_max_page(acc_type, hs_type, page_size)

    page_nrs = range(page_nr, max_page + 1)

    logging.info(f'scraping range({page_nr}-{max_page})')

    spawn_threads(process, page_nrs, acc_type=acc_type, hs_type=hs_type, out_file=out_file)


def find_max_page(acc_type, hs_type, page_size):
    # max on hs is currently 80_000 pages
    l, r, res = 1, 100_000, -1

    def give_first_idx(acc_type, hs_type, middle):
        page = get_hs_page(acc_type, hs_type, middle)
        extracted_records = extract_highscore_records(page)
        return -1 if not extracted_records else list(extracted_records.keys())[0]

    while l <= r:
        middle = (l + r) >> 1
        first_idx = retry(give_first_idx, acc_type, hs_type, middle)
        expected_idx = (middle - 1) * page_size + 1

        if first_idx == expected_idx:
            res = middle
            l = middle + 1
        else:
            r = middle - 1
        logging.info(f'looking for max page size: ({l}-{r})')
    return res


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

    logging.info("done")
    sys.exit(0)
