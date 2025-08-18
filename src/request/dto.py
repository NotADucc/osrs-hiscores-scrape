from dataclasses import dataclass

from src.request.common import HSAccountTypes, HSType


@dataclass
class GetMaxHighscorePageRequest:
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetMaxHighscorePageResult:
    page_nr: int
    rank_nr: int


@dataclass
class GetHighscorePageRequest:
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetPlayerRequest:
    username: str
    account_type: HSAccountTypes
