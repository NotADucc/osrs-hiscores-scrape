from dataclasses import dataclass
from typing import Callable

from src.request.common import HSAccountTypes, HSType


@dataclass
class GetMaxHighscorePageRequest:
    """ Request object for fetching the maximum hiscore page. """
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetMaxHighscorePageResult:
    """ Result object containing the highest hiscore page. """
    page_nr: int
    rank_nr: int


@dataclass
class GetFilteredPageRangeRequest:
    """ Request object for fetching the filtered page range. """
    hs_type: HSType
    predicate: Callable[[int], bool]
    account_type: HSAccountTypes


@dataclass
class GetFilteredPageRangeResult:
    """ Result object containing the filtered page range. """
    start_page: int
    start_rank: int
    end_page: int
    end_rank: int


@dataclass
class GetHighscorePageRequest:
    """ Request object for fetching the hiscore page. """
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetPlayerRequest:
    """ Request object for fetching a player record. """
    username: str
    account_type: HSAccountTypes
