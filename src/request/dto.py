from dataclasses import dataclass
from typing import Callable

from src.request.common import HSAccountTypes, HSType


@dataclass
class GetMaxHighscorePageRequest:
    """
    Request object for fetching the maximum hiscore page.

    Attributes:
        hs_type (HSType): The hiscore category.
        account_type (HSAccountTypes): The account type.
    """
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetMaxHighscorePageResult:
    """
    Result object containing the highest hiscore page.

    Attributes:
        page_nr (int): The page index (1-based).
        rank_nr (int): The last rank number present on the page.
    """
    page_nr: int
    rank_nr: int


@dataclass
class GetFilteredPageRangeRequest:
    """
    Request object for fetching the filtered page range.
    """
    hs_type: HSType
    predicate: Callable[[int], bool]
    account_type: HSAccountTypes
    

@dataclass
class GetFilteredPageRangeResult:
    """
    Result object containing the filtered page range.

    Attributes:
        start_page (int): The start page index (1-based).
        start_rank (int): The starting rank on this page.
        end_page (int): The end page index (1-based).
        end_rank (int): The ending rank on this page.
    """
    start_page: int
    start_rank: int
    end_page: int
    end_rank: int


@dataclass
class GetHighscorePageRequest:
    """
    Request object for fetching the hiscore page.

    Attributes:
        page_num (int): The page number.
        hs_type (HSType): The hiscore category.
        account_type (HSAccountTypes): The account type.
    """
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetPlayerRequest:
    """
    Request object for fetching a player record.

    Attributes:
        username (str): The players username.
        account_type (HSAccountTypes): The account type.
    """
    username: str
    account_type: HSAccountTypes
