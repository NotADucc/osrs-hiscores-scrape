from typing import List

from ..request.constants import HS_PAGE_SIZE
from ..request.dto import (GetFilteredPageRangeRequest,
                           GetMaxHighscorePageRequest)
from ..request.request import Requests
from .records import HSCategoryJob


async def get_hs_page_job(req: Requests, start_rank: int, end_rank: int, max_page_req: GetMaxHighscorePageRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves the maximum available page and rank.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page, end_page = _extract_page_nr_from_rank(
        start_rank=start_rank, end_rank=end_rank)

    res = await req.get_max_page(max_page_req=max_page_req)
    max_page_page, max_page_rank = res.page_nr, res.rank_nr

    if end_rank <= 0 or max_page_rank < end_rank:
        end_page = max_page_page
        end_rank = max_page_rank

    if start_rank > end_rank:
        return []

    return [
        HSCategoryJob(
            priority=page_num,
            page_num=page_num,
            start_rank=start_rank if page_num == start_page
                else (page_num - 1) * HS_PAGE_SIZE + 1,  # nopep8
            end_rank=end_rank if page_num == end_page
                else (page_num - 1) * HS_PAGE_SIZE + HS_PAGE_SIZE,  # nopep8
            account_type=max_page_req.account_type,
            hs_type=max_page_req.hs_type,
            start_idx=(start_rank - 1) % HS_PAGE_SIZE if page_num == start_page
                else 0,  # nopep8
            end_idx=(end_rank - 1) % HS_PAGE_SIZE + 1 if page_num == end_page
                else HS_PAGE_SIZE,  # nopep8
        )
        for page_num in range(start_page, end_page + 1)
    ]


async def get_hs_filtered_job(req: Requests, start_rank: int, end_rank: int, page_range_req: GetFilteredPageRangeRequest) -> List[HSCategoryJob]:
    """
    Generate jobs for fetching OSRS hiscore pages within a rank range.

    This function calculates which hiscore pages correspond to the given
    rank range, and retrieves a range based on a given predicate.

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    start_page, end_page = _extract_page_nr_from_rank(
        start_rank=start_rank, end_rank=end_rank)

    page_range = await req.get_filtered_page_range(page_range_req=page_range_req)
    filter_start_page, filter_start_rank = page_range.start_page, page_range.start_rank
    filter_end_page, filter_end_rank = page_range.end_page, page_range.end_rank

    if filter_start_rank > start_rank:
        start_page = filter_start_page
        start_rank = filter_start_rank

    if end_rank <= 0 or filter_end_rank < end_rank:
        end_page = filter_end_page
        end_rank = filter_end_rank

    if start_rank > end_rank:
        return []

    return [
        HSCategoryJob(
            priority=page_num,
            page_num=page_num,
            start_rank=start_rank if page_num == start_page
                else (page_num - 1) * HS_PAGE_SIZE + 1,  # nopep8
            end_rank=end_rank if page_num == end_page
                else (page_num - 1) * HS_PAGE_SIZE + HS_PAGE_SIZE,  # nopep8
            account_type=page_range_req.account_type,
            hs_type=page_range_req.filter_entry.hstype,
            start_idx=(start_rank - 1) % HS_PAGE_SIZE if page_num == start_page
                else 0,  # nopep8
            end_idx=(end_rank - 1) % HS_PAGE_SIZE + 1 if page_num == end_page
                else HS_PAGE_SIZE,  # nopep8
        )
        for page_num in range(start_page, end_page + 1)
    ]


def _extract_page_nr_from_rank(start_rank: int, end_rank: int) -> tuple[int, int]:
    """
    Converts rank ranges into page numbers

    Raises:
        ValueError: If `start_rank` is less than 1, or if
            `start_rank > end_rank` when `end_rank` > 0.
    """
    if start_rank < 1:
        raise ValueError("Start rank is smaller than 1")

    if end_rank > 0 and start_rank > end_rank:
        raise ValueError("Start rank is greater than end rank")

    start_page = (start_rank - 1) // 25 + 1
    end_page = (end_rank - 1) // 25 + 1

    return (start_page, end_page)
