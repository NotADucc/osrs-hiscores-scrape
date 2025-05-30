from fake_useragent import UserAgent
from request.common import HSCategoryMapper, IsRateLimited, RequestFailed, HSLookup, HSApi

import requests
from bs4 import BeautifulSoup
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


def lookup_scrape(name: str, account_type: HSLookup) -> str:
    params = {'user1': name}
    page = https_request(account_type.personal(), params)
    return page


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


def extract_stats(page: bytes) -> dict:
    soup = BeautifulSoup(page, "html.parser")
    body = soup.find(id='contentHiscores')
    result = {}

    categories = body.find_all('tr')
    categories = categories[3:]

    skills = True
    for category in categories:
        soup = category.find_all('td')
        if len(soup) == 0:
            skills = False
            continue

        name = category.find('a').text.strip()
        if skills:
            result[name] = {
                'rank': int(soup[-3].text.replace(',', '').strip()),
                'lvl': int(soup[-2].text.replace(',', '').strip()),
                'xp': int(soup[-1].text.replace(',', '').strip())
            }
        else:
            result[name] = {
                'rank': int(soup[-2].text.replace(',', '').strip()),
                'score': int(soup[-1].text.replace(',', '').strip())
            }

    return result


def extract_highscore_records(page: bytes) -> dict:
    soup = BeautifulSoup(page, "html.parser")
    scores = soup.find_all(class_='personal-hiscores__row')

    result = {}

    for score in scores:
        td_right = score.find_all('td', class_='right')

        rank = int(td_right[0].text.replace(',', '').strip())
        username = score.find('td', class_='left').a.text.strip()
        score = int(td_right[1].text.replace(',', '').strip())
        result[rank] = {
            'username': username,
            'score': score
        }

    return result