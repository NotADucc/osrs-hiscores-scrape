import argparse
import datetime
import sys
import threading

from request.extract import extract_highscore_records
from request.request import Requests
from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from request.common import CategoryInfo, HSCategoryMapper, HSLookup
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()
account_type = HSLookup.regular


def process(page_nr: int, **args: dict) -> None:
    hs_type, category_info, temp_file, req = args["hs_type"], args[
        "category_info"], args["temp_file"], args["req"]
    try:
        page = retry(req.get_hs_page, account_type=account_type,
                     hs_type=hs_type, page_nr=page_nr)
        extracted_records = extract_highscore_records(page)

        with file_lock:
            with open(temp_file, "a") as f:
                for record in extracted_records:
                    f.write(f'{record}\n')
                    category_info.add(record=record)

        logger.info(f'finished page: {page_nr}')
    except Exception as err:
        print(err)


def main(out_file: str, proxy_file: str | None, hs_type: HSCategoryMapper):
    if proxy_file is not None:
        with open(proxy_file, "r") as f:
            proxies = f.read().splitlines()
    else:
        proxies = []

    req = Requests(proxies)

    max_page = req.find_max_page(account_type, hs_type)

    page_nrs = range(1, max_page + 1)

    logger.info(f'scraping {page_nrs}')

    category_info = CategoryInfo(
        name=hs_type.name, ts=datetime.datetime.now(datetime.timezone.utc))

    temp_file = out_file.split('.')[0] + ".temp"
    spawn_threads(process, page_nrs, hs_type=hs_type,
                  category_info=category_info, temp_file=temp_file, req=req)

    with file_lock:
        with open(out_file, "a") as f:
            f.write(f'{category_info}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--proxy-file', help="Path to the proxy file")
    parser.add_argument('--hs-type', required=True,
                        type=HSCategoryMapper.from_string, choices=list(HSCategoryMapper), help="Hiscore category it should pull from")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.out_file, args.proxy_file, args.hs_type)

    logger.info("done")
    sys.exit(0)
