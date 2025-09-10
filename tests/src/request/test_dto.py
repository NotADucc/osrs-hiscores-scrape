from typing import Callable
import pytest

from src.request.common import HSAccountTypes, HSType
from src.request.dto import GetFilteredPageRangeRequest, GetFilteredPageRangeResult, GetHighscorePageRequest, GetMaxHighscorePageRequest, GetMaxHighscorePageResult, GetPlayerRequest, HSFilterEntry


@pytest.mark.parametrize(
    "hs_type, predicate",
    [
        (HSType.agility, lambda val: val > 50),
        (HSType.combat, lambda val: val > 50.0),
    ],
)
def test_hs_filter_entry_value(hs_type: HSType, predicate: Callable[[int | float], bool]):
    hs_filter = HSFilterEntry(hstype=hs_type, predicate=predicate)

    assert hs_filter.hstype == hs_type
    assert hs_filter.predicate == predicate

@pytest.mark.parametrize(
    "hs_type, account_type",
    [
        (HSType.agility, HSAccountTypes.regular),
        (HSType.combat,  HSAccountTypes.pure),
    ],
)
def test_get_max_hs_request_value(hs_type: HSType, account_type: HSAccountTypes):
    max_page_request = GetMaxHighscorePageRequest(hs_type=hs_type, account_type=account_type)

    assert max_page_request.hs_type == hs_type
    assert max_page_request.account_type == account_type

@pytest.mark.parametrize(
    "page_nr, rank_nr",
    [
        (-1, -1),
        (0, 0),
        (1, 1),
        (2, 10),
        (1_000_000, 1_000_000),
    ],
)
def test_get_max_hs_result_value(page_nr: int, rank_nr: int):
    max_page_result = GetMaxHighscorePageResult(page_nr=page_nr, rank_nr=rank_nr)

    assert max_page_result.page_nr == page_nr
    assert max_page_result.rank_nr == rank_nr


@pytest.mark.parametrize(
    "filter_entry, account_type",
    [
        (HSFilterEntry(hstype=HSType.agility, predicate=lambda val: val > 50), HSAccountTypes.regular),
    ],
)
def test_get_filtered_page_range_request_value(filter_entry: HSFilterEntry, account_type: HSAccountTypes):
    filter_page_request = GetFilteredPageRangeRequest(filter_entry=filter_entry, account_type=account_type)

    assert filter_page_request.filter_entry == filter_entry
    assert filter_page_request.account_type == account_type

@pytest.mark.parametrize(
    "start_page, start_rank, end_page, end_rank",
    [
        (-1, -1, -1, -1),
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (1, 1, 1, 25),
        (2, 50, 1, 25),
        (3, 50, 2, 25),
    ],
)
def test_get_filtered_page_range_result_value(start_page: int, start_rank: int, end_page: int, end_rank: int):
    filter_page_result = GetFilteredPageRangeResult(start_page=start_page, start_rank=start_rank, end_page=end_page, end_rank=end_rank)

    assert filter_page_result.start_page == start_page
    assert filter_page_result.start_rank == start_rank
    assert filter_page_result.end_page == end_page
    assert filter_page_result.end_rank == end_rank

@pytest.mark.parametrize(
"page_num, hs_type, account_type",
[
    (-1, HSType.overall, HSAccountTypes.regular),
    (0, HSType.overall, HSAccountTypes.regular),
    (1, HSType.overall, HSAccountTypes.regular),
],
)
def test_get_hs_page_request_value(page_num: int, hs_type: HSType, account_type: HSAccountTypes):
    hs_page_request = GetHighscorePageRequest(page_num=page_num, hs_type=hs_type, account_type=account_type)

    assert hs_page_request.page_num == page_num
    assert hs_page_request.hs_type == hs_type
    assert hs_page_request.account_type == account_type

@pytest.mark.parametrize(
"username, account_type",
[
    ("", HSAccountTypes.regular),
    (" ", HSAccountTypes.regular),
    ("\n", HSAccountTypes.regular),
    ("\t", HSAccountTypes.regular),
    ("test", HSAccountTypes.regular),
    ("1234567890", HSAccountTypes.regular),
    ("abcdefghijklmnopqrstuvwxyz", HSAccountTypes.regular),
],
)
def test_get_player_request_value(username: str, account_type: HSAccountTypes):
    player_request = GetPlayerRequest(username=username, account_type=account_type)

    assert player_request.username == username
    assert player_request.account_type == account_type