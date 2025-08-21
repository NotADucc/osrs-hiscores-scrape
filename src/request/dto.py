from dataclasses import dataclass

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
