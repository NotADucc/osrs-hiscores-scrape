from fake_useragent import UserAgent
from request.common import HSCategoryMapper, IsRateLimited, RequestFailed, HSLookup, HSApi

import requests
from bs4 import BeautifulSoup
from request.extract import extract_highscore_records
from util.log import get_logger
from util.retry_handler import retry

logger = get_logger()


def find_max_page(account_type: HSLookup, hs_type: HSCategoryMapper) -> int:
    # max on hs is currently 80_000 pages
    l, r, res, page_size = 1, 100_000, -1, 25

    def give_first_idx(account_type, hs_type, middle):
        page = get_hs_page(account_type, hs_type, middle)
        extracted_records = extract_highscore_records(page)
        return -1 if not extracted_records else list(extracted_records.keys())[0]

    while l <= r:
        middle = (l + r) >> 1
        first_idx = retry(give_first_idx, account_type=account_type,
                          hs_type=hs_type, middle=middle)
        expected_idx = (middle - 1) * page_size + 1

        if first_idx == expected_idx:
            res = middle
            l = middle + 1
        else:
            r = middle - 1
        logger.info(f'looking for max page size: ({l}-{r})')
    return res


def get_hs_page(account_type: HSLookup, hs_type: HSCategoryMapper, page_nr: int = 1) -> bytes:
    params = {'category_type': hs_type.get_category(),
              'table': hs_type.value, 'page': page_nr, }
    page = https_request(account_type.overall(), params)
    return page


def lookup(name: str, account_type: HSApi) -> str:
    params = {'player': name}
    csv = https_request(account_type.value, params)
    return csv

def https_request(url: str, params: dict) -> str:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
        "Content-Type": "text/html",
        'User-Agent': UserAgent().random,
    }

    resp = requests.get(url, headers=headers, params=params)

    text = resp.text.replace('Ā', ' ').replace('\xa0', ' ')

    if is_rate_limited(text):
        raise IsRateLimited(
            f"limited on \'{url}\'", details={"params": params})

    if resp.status_code == 200:
        return text

    raise RequestFailed(f"failed on \'{url}\'", details={
                        "code": resp.status_code, "params": params})


def is_rate_limited(page: bytes):
    return "your IP has been temporarily blocked" in BeautifulSoup(page, "html.parser").text