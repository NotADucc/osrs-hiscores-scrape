import datetime
import threading
from typing import Dict

from aiohttp import ClientConnectionError, ClientSession
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from request.common import get_page_size
from request.dto import (GetHighscorePageRequest, GetMaxHighscorePageRequest,
                         GetMaxHighscorePageResult, GetPlayerRequest)
from request.errors import (IsRateLimited, NotFound, ParsingFailed,
                            RequestFailed, ServerBusy)
from request.results import CategoryRecord, PlayerRecord
from util.log import get_logger
from util.retry_handler import retry

logger = get_logger()
proxy_lock = threading.Lock()
session_lock = threading.Lock()


class Requests():
    def __init__(self, session: ClientSession, proxy_list:  list | None = None):
        self.session = session
        self.proxy_list = proxy_list
        self.proxy_idx = 0

    def remove_cookies(self) -> ClientSession:
        with session_lock:
            self.session.cookie_jar.clear()

    def get_session(self) -> ClientSession:
        return self.session

    def get_proxy(self) -> dict | None:
        if not self.proxy_list or len(self.proxy_list) == 0:
            return None

        with proxy_lock:
            proxy = self.proxy_list[self.proxy_idx]
            self.proxy_idx = (self.proxy_idx + 1) % len(self.proxy_list)

        return proxy

    async def get_max_page(self, input: GetMaxHighscorePageRequest) -> GetMaxHighscorePageResult:
        # max on hs is currently 80_000 pages
        l, r, res, PAGE_SIZE = 1, 100_000, 1, get_page_size()

        async def get_last_idx(hs_request: GetHighscorePageRequest):
            extracted_records = await self.get_hs_page(hs_request)
            return -1 if not extracted_records else extracted_records[-1].rank

        while l <= r:
            middle = (l + r) >> 1
            last_idx = await retry(
                get_last_idx,
                hs_request=GetHighscorePageRequest(
                    page_num=middle, hs_type=input.hs_type, account_type=input.account_type)
            )
            expected_first_idx = (middle - 1) * PAGE_SIZE + 1

            if last_idx >= expected_first_idx:
                res = middle
                l = middle + 1
            else:
                r = middle - 1
            logger.info(f'page range: ({l}-{r})')

        last_rank = await get_last_idx(hs_request=GetHighscorePageRequest(page_num=res, hs_type=input.hs_type, account_type=input.account_type))
        logger.info(f"Max page found: {res}")
        return GetMaxHighscorePageResult(page_nr=res, rank_nr=last_rank)

    async def get_user_stats(self, input: GetPlayerRequest) -> PlayerRecord:
        csv = (await self.lookup(input)).split('\n')
        return PlayerRecord(username=input.username, csv=csv, ts=datetime.datetime.now(datetime.timezone.utc))

    async def get_hs_page(self, input: GetHighscorePageRequest) -> list[CategoryRecord]:
        params = {'category_type': input.hs_type.get_category(),
                  'table': input.hs_type.get_category_value(), 'page': input.page_num, }
        page = await self.https_request(input.account_type.lookup_overall(), params)
        return Requests.extract_highscore_records(page)

    async def lookup(self, input: GetPlayerRequest) -> str:
        return await self.https_request(input.account_type.api_csv(), {'player': input.username})

    async def https_request(self, url: str, params: Dict[str, str]) -> str:
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
            "Content-Type": "text/html",
            'User-Agent': UserAgent().random,
        }

        proxy = self.get_proxy()
        session = self.get_session()

        try:
            async with session.get(url, headers=headers, params=params, proxy=proxy, timeout=30) as resp:
                text = await resp.text()
                if Requests.is_rate_limited(text):
                    raise IsRateLimited(
                        f"limited on '{url}'", details={"params": params, "proxy": proxy})

                if resp.status == 404:
                    raise NotFound(f"Not found", details={
                        "params": params, "proxy": proxy})

                if resp.status == 200:
                    return text

                raise RequestFailed(f"failed on '{url}'", details={
                                    "code": resp.status, "params": params, "proxy": proxy})
        except TimeoutError:
            raise ServerBusy("timed out")
        except ClientConnectionError as e:
            raise RequestFailed(f"client connection error: {e}")

    @staticmethod
    def is_rate_limited(page: str) -> bool:
        return "your IP has been temporarily blocked" in BeautifulSoup(page, "html.parser").text

    @staticmethod
    def extract_highscore_records(page: str) -> list[CategoryRecord]:
        soup = BeautifulSoup(page, "html.parser")
        table = soup.find_all(class_='personal-hiscores__table')

        if len(table) == 0:
            raise ParsingFailed("Could not find hiscore table")

        records = table[0].find_all(class_='personal-hiscores__row')

        result = []

        for record in records:
            td_right = record.find_all('td', class_='right')

            rank = int(td_right[0].text.replace(',', '').strip())
            # some names contain special char - "non-breaking space."
            username = record.find('td', class_='left').a.text.strip().replace(
                'Ā', ' ').replace('\xa0', ' ')
            score = int(td_right[1].text.replace(',', '').strip())
            result.append(CategoryRecord(
                rank=rank, score=score, username=username))

        return result
