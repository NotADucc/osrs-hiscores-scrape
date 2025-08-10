from dataclasses import dataclass
from request.common import HSAccountTypes, HSType


@dataclass
class GetMaxHighscorePageRequest:
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetHighscorePageRequest:
    page_num: int
    hs_type: HSType
    account_type: HSAccountTypes


@dataclass
class GetPlayerRequest:
    username: str
    account_type: HSAccountTypes
