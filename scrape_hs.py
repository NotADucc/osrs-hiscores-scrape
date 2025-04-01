import argparse
import sys
import threading

from util.retry_handler import retry
from util.threading_handler import spawn_threads
from request.common import HSOverall, HSOverallTableMapper
from request.request import find_max_page, get_hs_page, extract_highscore_records
from util.log import get_logger

logger = get_logger()
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

        logger.info(f'finished page: {page_nr}')
    except Exception as err:
        print(err)


def main(out_file, acc_type, hs_type, page_nr, page_size=25):
    max_page = find_max_page(acc_type, hs_type, page_size)

    page_nrs = range(page_nr, max_page + 1)

    logger.info(f'scraping range({page_nr}-{max_page})')

    spawn_threads(process, page_nrs, acc_type=acc_type,
                  hs_type=hs_type, out_file=out_file)


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

    logger.info("done")
    sys.exit(0)
