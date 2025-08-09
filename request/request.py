import datetime
from fake_useragent import UserAgent

import threading
import requests
from bs4 import BeautifulSoup
from request.dto import GetHighscorePageRequest, GetMaxHighscorePageRequest, GetPlayerRequest
from request.errors import IsRateLimited, PlayerDoesNotExist, RequestFailed
from request.results import CategoryRecord, PlayerRecord
from util.log import get_logger
from util.retry_handler import retry

logger = get_logger()
proxy_lock = threading.Lock()


class Requests():
    def __init__(self, proxy_list:  list | None = None):
        self.proxy_list = proxy_list
        self.proxy_idx = 0

    def get_proxies(self) -> dict | None:
        if not self.proxy_list or len(self.proxy_list) == 0:
            return None

        with proxy_lock:
            proxy = self.proxy_list[self.proxy_idx]
            self.proxy_idx = (self.proxy_idx + 1) % len(self.proxy_list)

        return {
            "http": proxy,
            "https": proxy,
        }

    def find_max_page(self, input: GetMaxHighscorePageRequest) -> int:
        # max on hs is currently 80_000 pages
        l, r, res, page_size = 1, 100_000, -1, 25

        def give_first_idx(account_type, hs_type, middle):
            page = self.get_hs_page(account_type, hs_type, middle)
            extracted_records = Requests.extract_highscore_records(page)
            return -1 if not extracted_records else extracted_records[0].rank

        while l <= r:
            middle = (l + r) >> 1
            first_idx = retry(give_first_idx, account_type=input.account_type,
                              hs_type=input.hs_type, middle=middle)
            expected_idx = (middle - 1) * page_size + 1

            if first_idx == expected_idx:
                res = middle
                l = middle + 1
            else:
                r = middle - 1
            logger.info(f'page range: ({l}-{r})')
        return res

    # def get_user_stats(self, name: str, account_type: HSAccountTypes, **kwargs) -> PlayerRecord:
    def get_user_stats(self, input: GetPlayerRequest) -> PlayerRecord:
        csv = self.lookup(input).split('\n')
        return PlayerRecord(username=input.username, csv=csv, ts=datetime.datetime.now(datetime.timezone.utc))

    def get_hs_page(self, input: GetHighscorePageRequest) -> list[CategoryRecord]:
        params = {'category_type': input.hs_type.get_category(),
                  'table': input.hs_type.get_category_value(), 'page': input.page_num, }
        page = self.https_request(input.account_type.lookup_overall(), params)
        return Requests.extract_highscore_records(page)

    def lookup(self, input: GetPlayerRequest) -> str:
        params = {'player': input.username}
        res = self.https_request(input.account_type.api_csv(), params)
        return res

    def https_request(self, url: str, params: dict) -> str:
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
            "Content-Type": "text/html",
            'User-Agent': UserAgent().random,
        }

        proxies = self.get_proxies()
        resp = requests.get(url, headers=headers,
                            params=params, proxies=proxies)

        text = resp.text.replace('Ā', ' ').replace('\xa0', ' ')

        if Requests.is_rate_limited(text):
            raise IsRateLimited(
                f"limited on \'{url}\'", details={"params": params, "proxies": proxies})

        if ('player' in params and not Requests.does_player_exist(params.get('player'), text)) or resp.status_code == 404:
            raise PlayerDoesNotExist(f"Player does not exist", details={
                                     "params": params, "proxies": proxies})

        if resp.status_code == 200:
            return text

        raise RequestFailed(f"failed on \'{url}\'", details={
                            "code": resp.status_code, "params": params, "proxies": proxies})
    
    @staticmethod
    def is_rate_limited(page: bytes) -> bool:
        return "your IP has been temporarily blocked" in BeautifulSoup(page, "html.parser").text
    
    @staticmethod
    def does_player_exist(name: str, page: bytes) -> bool:
        return not f"No player \"{name}\" found" in BeautifulSoup(page, "html.parser").text

    @staticmethod
    def extract_highscore_records(page: bytes) -> list[CategoryRecord]:
        soup = BeautifulSoup(page, "html.parser")
        scores = soup.find_all(class_='personal-hiscores__row')

        result = []

        for score in scores:
            td_right = score.find_all('td', class_='right')

            rank = int(td_right[0].text.replace(',', '').strip())
            username = score.find('td', class_='left').a.text.strip()
            score = int(td_right[1].text.replace(',', '').strip())
            result.append(CategoryRecord(
                rank=rank, score=score, username=username))

        return result