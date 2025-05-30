import argparse
import sys
import threading

from util.guard_clause_handler import running_script_not_in_cmd_guard
from util.retry_handler import retry
from util.threading_handler import spawn_threads
from request.common import HSCategoryMapper, HSLookup
from request.request import find_max_page, get_hs_page, extract_highscore_records
from util.log import get_logger

logger = get_logger()
file_lock = threading.Lock()


def process(page_nr: int, **args: dict) -> None:
    hs_type, category_info = args["hs_type"], args["category_info"]
    try:
        page = retry(get_hs_page, account_type=HSLookup.regular,
                     hs_type=hs_type, page_nr=page_nr)
        extracted_records = extract_highscore_records(page)

        with file_lock:
            for key, value in extracted_records.items():
                category_info['count'] += 1
                category_info['total_score'] += value['score']
                if category_info['max']['score'] < value['score'] :
                    category_info['max']['name'] = value['username']
                    category_info['max']['score'] = value['score']

                if category_info['min']['score'] > value['score'] :
                    category_info['min']['name'] = value['username']
                    category_info['min']['score'] = value['score']

        logger.info(f'finished page: {page_nr}')
    except Exception as err:
        print(err)


def main(out_file, hs_type):
    max_page = find_max_page(HSLookup.regular, hs_type)

    page_nrs = range(1, max_page + 1)

    logger.info(f'scraping range({1}-{max_page})')

    category_info = {
        'count': 0,
        'total_score' : 0,
        'max': {
            'name': None,
            'score': float('-inf'),
        },
        'min': {
            'name': None,
            'score': float('inf'),
        },
    }

    spawn_threads(process, page_nrs, hs_type=hs_type, category_info=category_info)

    with file_lock:
        with open(out_file, "a") as f:
            f.write('%s\n' % category_info)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-file', required=True,
                        help="Path to the output file")
    parser.add_argument('--hs-type', required=True,
                        type=HSCategoryMapper.from_string, choices=list(HSCategoryMapper), help="Hiscore category it should pull from")

    running_script_not_in_cmd_guard(parser)
    args = parser.parse_args()

    main(args.out_file, args.hs_type)

    logger.info("done")
    sys.exit(0)
