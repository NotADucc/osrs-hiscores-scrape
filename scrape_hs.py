import argparse
import sys
import threading

from request.extract import extract_highscore_records
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from request.common import HSCategoryMapper, HSLookup
from request.request import Requests
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def process(page_nr: int, **args: dict) -> None:
    account_type, hs_type, out_file, req = args["account_type"], args[
        "hs_type"], args["out_file"], args["request"]
    try:
        page = retry(req.get_hs_page, account_type=account_type,
                     hs_type=hs_type, page_nr=page_nr)
        extracted_records = extract_highscore_records(page)

        with file_lock:
            with open(out_file, "a") as f:
                for key, value in extracted_records.items():
                    f.write('%s,%s\n' % (key, value['username']))

        logger.info(f'finished page: {page_nr}')
    except Exception as err:
        print(err)


def main(out_file: str, proxy_file: str | None, account_type: HSLookup, hs_type: HSCategoryMapper, page_nr: int):
    if proxy_file is not None:
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    req = Requests(proxies)

    max_page = req.find_max_page(account_type, hs_type)

    page_nrs = range(page_nr, max_page + 1)

    logger.info(f'scraping {page_nrs}')

    spawn_threads(process, page_nrs, account_type=account_type,
                  hs_type=hs_type, out_file=out_file, request=req)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--account-type', default='regular',
                        type=HSLookup.from_string, choices=list(HSLookup), help="Account type it should pull from (default: 'regular')")
    parser.add_argument('--hs-type', default='overall',
                        type=HSCategoryMapper.from_string, choices=list(HSCategoryMapper), help="Hiscore category it should pull from (default: 'overall')")
    parser.add_argument('--page-nr', default=1, type=int,
                        help="Hiscore page number it should start at")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.out_file, args.proxy_file,
         args.account_type, args.hs_type, args.page_nr)

    logger.info("done")
    sys.exit(0)
