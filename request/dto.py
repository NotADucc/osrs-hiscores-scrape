from dataclasses import dataclass
from request.common import HSAccountTypes, HSCategoryMapper

@dataclass
class GetMaxHighscorePageRequest:
    hs_type: HSCategoryMapper
    account_type: HSAccountTypes

@dataclass
class GetHighscorePageRequest:
    page_num: int
    hs_type: HSCategoryMapper
    account_type: HSAccountTypes


@dataclass
class GetPlayerRequest:
    username: str
    account_type: HSAccountTypes
