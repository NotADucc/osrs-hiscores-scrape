import datetime
import threading
from typing import Any, Callable, Dict

from aiohttp import ClientConnectionError, ClientSession, ClientTimeout
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent

from src.request.common import HS_PAGE_SIZE, MAX_CATEGORY_SIZE, HSType
from src.request.dto import (GetFilteredPageRangeRequest,
                             GetFilteredPageRangeResult,
                             GetHighscorePageRequest,
                             GetMaxHighscorePageRequest,
                             GetMaxHighscorePageResult, GetPlayerRequest)
from src.request.errors import (IsRateLimited, NotFound, ParsingFailed,
                                RequestFailed, ServerBusy)
from src.request.results import CategoryRecord, PlayerRecord
from src.stats.common import calc_lvl
from src.util.log import get_logger
from src.util.predicate_utils import get_comparison
from src.util.retry_handler import retry

logger = get_logger()


class Requests():
    """
    Wrapper for an aiohttp ClientSession that optionally supports
    rotating proxies and cookie management.
    """

    def __init__(self, session: ClientSession, proxy_list: list[str] | None = None):
        self.session = session
        self.proxy_list = proxy_list
        self._proxy_idx = 0
        self._proxy_lock = threading.Lock()
        self._session_lock = threading.Lock()

    def remove_cookies(self) -> None:
        """ Clear all cookies in the current session. """
        with self._session_lock:
            self.session.cookie_jar.clear()

    def get_session(self) -> ClientSession:
        """ Get the current ClientSession. """
        return self.session

    def get_proxy(self) -> str | None:
        """ Get the next proxy in the rotation. """
        if not self.proxy_list or len(self.proxy_list) == 0:
            return None

        with self._proxy_lock:
            proxy = self.proxy_list[self._proxy_idx]
            self._proxy_idx = (self._proxy_idx + 1) % len(self.proxy_list)

        return proxy

    async def get_max_page(self, input: GetMaxHighscorePageRequest) -> GetMaxHighscorePageResult:
        """
        Determine the maximum available highscore page and its last rank.

        Raises:
            Any exceptions raised by `self.get_hs_page` or `retry`.
        """

        l, r, res = 1, MAX_CATEGORY_SIZE, 1

        while l <= r:
            middle = (l + r) >> 1

            logger.debug(f'current range: ({l}-{r}) middle: {middle}')

            first_rank = await retry(
                self.get_first_rank,
                hs_request=GetHighscorePageRequest(
                    page_num=middle, hs_type=input.hs_type, account_type=input.account_type)
            )
            expected_first_rank = (middle - 1) * HS_PAGE_SIZE + 1

            if first_rank == expected_first_rank:
                res = middle
                l = middle + 1
            else:
                r = middle - 1

        last_rank = await self.get_last_rank(hs_request=GetHighscorePageRequest(page_num=res, hs_type=input.hs_type, account_type=input.account_type))
        logger.info(f"Max page found: {res}")
        return GetMaxHighscorePageResult(page_nr=res, rank_nr=last_rank)

    async def get_filtered_page_range(self, input: GetFilteredPageRangeRequest) -> GetFilteredPageRangeResult:
        """
        Determine the highscore ranges on a given predicate.

        Raises:
            Any exceptions raised by `self.get_hs_page` or `retry`.
        """

        async def binary_search_hs_page(predicate: Callable[[list[int]], bool], left_bias: bool) -> int:
            l, r, res = 1, MAX_CATEGORY_SIZE, 1
            predicate_bias = get_comparison(predicate) in ("<", "<=", "==")
            while l <= r:
                middle = (l + r) >> 1

                records = await retry(
                    self.get_hs_page,
                    hs_request=GetHighscorePageRequest(
                        page_num=middle, hs_type=input.hs_type, account_type=input.account_type)
                )
                expected_first_rank = (middle - 1) * HS_PAGE_SIZE + 1

                logger.debug(f'current range: ({l}-{r}) middle: {middle}')

                if not records or records[0].rank != expected_first_rank:
                    r = middle - 1
                    continue

                scores = _extract_record_scores(
                    records=records, hs_type=input.hs_type)

                if predicate(scores):
                    res = middle
                    if left_bias:
                        r = middle - 1
                    else:
                        l = middle + 1
                else:
                    if predicate_bias:
                        l = middle + 1
                    else:
                        r = middle - 1

            return res

        sign = get_comparison(input.predicate)
        predicate: Callable = lambda values: any(
            input.predicate(v) for v in values)

        if sign in ("<", "<="):
            start_page = await binary_search_hs_page(
                predicate=predicate,
                left_bias=True
            )
            end_page = (await self.get_max_page(
                input=GetMaxHighscorePageRequest(
                    account_type=input.account_type,
                    hs_type=input.hs_type
                )
            )).page_nr
        elif sign in ("=="):
            start_page = await binary_search_hs_page(
                predicate=predicate,
                left_bias=True
            )
            end_page = await binary_search_hs_page(
                predicate=predicate,
                left_bias=False
            )
        elif sign in (">", ">="):
            start_page = 1
            end_page = await binary_search_hs_page(
                predicate=predicate,
                left_bias=False
            )
        else:
            raise ValueError(f"Unsupported operator: '{sign}'")

        start_rank = await self.get_first_rank(hs_request=GetHighscorePageRequest(page_num=start_page, hs_type=input.hs_type, account_type=input.account_type))
        end_rank = await self.get_last_rank(hs_request=GetHighscorePageRequest(page_num=end_page, hs_type=input.hs_type, account_type=input.account_type))

        logger.info(
            f"Page range found: {start_page}-{end_page} ({start_rank}-{end_rank})")
        return GetFilteredPageRangeResult(start_page=start_page, start_rank=start_rank, end_page=end_page, end_rank=end_rank)

    async def get_user_stats(self, input: GetPlayerRequest) -> PlayerRecord:
        """ Fetch and parse a player's stats from OSRS hiscores. """
        csv = await self.https_request(input.account_type.api_csv(), {'player': input.username})
        csv = [line for line in csv.split('\n') if line]
        return PlayerRecord(username=input.username, csv=csv, ts=datetime.datetime.now(datetime.timezone.utc))

    async def get_hs_page(self, hs_request: GetHighscorePageRequest) -> list[CategoryRecord]:
        """ Fetch and parse a page of highscores for a specific category and account type. """
        params = {'category_type': hs_request.hs_type.get_category(),
                  'table': hs_request.hs_type.get_category_value(), 'page': hs_request.page_num, }
        page = await self.https_request(hs_request.account_type.lookup_overall(), params)
        return _extract_hs_page_records(page)

    async def https_request(self, url: str, params: Dict[str, Any]) -> str:
        """
        Perform an asynchronous HTTP GET request with optional proxy support.

        Raises:
            IsRateLimited: If the server response indicates rate limiting.
            NotFound: If the requested resource returns a 404 status.
            RequestFailed: For other non-200 HTTP responses or client connection errors.
            ServerBusy: If the request times out.
        """
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
            "Content-Type": "text/html",
            'User-Agent': UserAgent().random,
        }

        proxy = self.get_proxy()
        session = self.get_session()

        try:
            async with session.get(url, headers=headers, params=params, proxy=proxy, timeout=ClientTimeout(total=30)) as resp:
                text = await resp.text()
                if _is_rate_limited(text):
                    raise IsRateLimited(
                        f"rate limited: '{url}'", details={"url": resp.url, "params": params, "proxy": proxy})

                if resp.status == 404:
                    raise NotFound(f"Not found", details={
                        "params": params, "proxy": proxy})

                if resp.status == 200:
                    return text

                raise RequestFailed(f"failed on '{url}'", details={
                    "code": resp.status, "reason": resp.reason, "url": resp.url, "params": params, "proxy": proxy})
        except TimeoutError:
            raise ServerBusy("timed out")
        except ClientConnectionError as e:
            raise RequestFailed(f"client connection error: {e}")

    async def get_hs_ranks(self, hs_request: GetHighscorePageRequest) -> list[int]:
        """ Gets the ranks of a hs page, empty list if page doesnt exist """
        extracted_records = await self.get_hs_page(hs_request=hs_request)

        if not extracted_records:
            return []

        return [record.rank for record in extracted_records]

    async def get_first_rank(self, hs_request: GetHighscorePageRequest) -> int:
        """ Gets the first rank of a hs page, -1 if page doesnt exist """
        extracted_ranks = await self.get_hs_ranks(hs_request=hs_request)
        return extracted_ranks[0] if extracted_ranks else -1

    async def get_last_rank(self, hs_request: GetHighscorePageRequest) -> int:
        """ Gets the last rank of a hs page, -1 if page doesnt exist """
        extracted_ranks = await self.get_hs_ranks(hs_request=hs_request)
        return extracted_ranks[-1] if extracted_ranks else -1

    async def get_hs_scores(self, hs_request: GetHighscorePageRequest) -> list[int]:
        """ Gets the scores of a hs page, empty list if page doesnt exist """
        extracted_records = await self.get_hs_page(hs_request=hs_request)

        if not extracted_records:
            return []

        return _extract_record_scores(records=extracted_records, hs_type=hs_request.hs_type)

    async def get_first_score(self, hs_request: GetHighscorePageRequest) -> int:
        """ Gets the first score of a hs page, -1 if page doesnt exist """
        extracted_scores = await self.get_hs_scores(hs_request=hs_request)
        return extracted_scores[0] if extracted_scores else -1

    async def get_last_score(self, hs_request: GetHighscorePageRequest) -> int:
        """ Gets the last score of a hs page, -1 if page doesnt exist """
        extracted_scores = await self.get_hs_scores(hs_request=hs_request)
        return extracted_scores[-1] if extracted_scores else -1


def _is_rate_limited(page: str) -> bool:
    """ Check if a hiscore page indicates a rate limit has been triggered. """
    return "your IP has been temporarily blocked" in BeautifulSoup(page, "html.parser").text


def _extract_hs_page_records(page: str) -> list[CategoryRecord]:
    """
    Parse a hiscore page of OSRS personal highscores and extract rank, username, and score records.

    Raises:
        ParsingFailed: If the hiscore table cannot be found on the page.
    """
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find(class_='personal-hiscores__table')

    if not table or not isinstance(table, Tag):
        raise ParsingFailed("Could not find hiscore table")

    records = table.find_all(class_='personal-hiscores__row')

    result = []

    for record in records:
        td_right = record.find_all('td', class_='right')  # type: ignore

        rank = int(td_right[0].text.replace(',', '').strip())
        # some names contain special char - "non-breaking space."
        username = record.find('td', class_='left').a.text.strip().replace(  # type: ignore
            'Ā', ' ').replace('\xa0', ' ')  # type: ignore
        score = int(td_right[1].text.replace(',', '').strip())
        result.append(CategoryRecord(
            rank=rank, score=score, username=username))

    return result


def _extract_record_scores(records: list[CategoryRecord], hs_type: HSType) -> list[int]:
    return [
        calc_lvl(record.score, show_virtual_lvl=False) if hs_type.is_skill(
        ) else record.score
        for record in records
    ]
