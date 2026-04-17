from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osrs_hiscore_scrape.job.job_builder import (_extract_page_nr_from_rank,
                                                 get_hs_filtered_job,
                                                 get_hs_page_job)
from osrs_hiscore_scrape.request.dto import (GetFilteredPageRangeResult,
                                             GetMaxHighscorePageResult)
from osrs_hiscore_scrape.request.hs_types import HSAccountTypes
from osrs_hiscore_scrape.request.request import Requests


@pytest.mark.asyncio
async def test_get_hs_page_job(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_max_page_req = MagicMock()
    mock_max_page_req.account_type = HSAccountTypes.regular
    res = GetMaxHighscorePageResult(page_nr=2, rank_nr=50)

    with (
        patch.object(req, "get_max_page", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_page_job(req, start_rank=1, end_rank=-1, max_page_req=mock_max_page_req)

    mock_filter.assert_awaited_once_with(max_page_req=mock_max_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=-1)

    assert len(result) == 2
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25

    assert result[1].account_type == HSAccountTypes.regular
    assert result[1].priority == 2
    assert result[1].page_num == 2
    assert result[1].start_rank == 26
    assert result[1].end_rank == 50
    assert result[1].start_idx == 0
    assert result[1].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_page_job_end_rank_given(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_max_page_req = MagicMock()
    mock_max_page_req.account_type = HSAccountTypes.regular
    res = GetMaxHighscorePageResult(page_nr=2, rank_nr=50)

    with (
        patch.object(req, "get_max_page", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, 1)) as mock_extract
    ):

        result = await get_hs_page_job(req, start_rank=1, end_rank=25, max_page_req=mock_max_page_req)

    mock_filter.assert_awaited_once_with(max_page_req=mock_max_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=25)

    assert len(result) == 1
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_page_job_end_rank_adjusted(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_max_page_req = MagicMock()
    mock_max_page_req.account_type = HSAccountTypes.regular
    res = GetMaxHighscorePageResult(page_nr=2, rank_nr=40)

    with (
        patch.object(req, "get_max_page", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_page_job(req, start_rank=1, end_rank=50, max_page_req=mock_max_page_req)

    mock_filter.assert_awaited_once_with(max_page_req=mock_max_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=50)

    assert len(result) == 2
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25

    assert result[1].account_type == HSAccountTypes.regular
    assert result[1].priority == 2
    assert result[1].page_num == 2
    assert result[1].start_rank == 26
    assert result[1].end_rank == 40
    assert result[1].start_idx == 0
    assert result[1].end_idx == 15


@pytest.mark.asyncio
async def test_get_hs_page_job_start_rank_equals_end_rank(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_max_page_req = MagicMock()
    mock_max_page_req.account_type = HSAccountTypes.regular
    res = GetMaxHighscorePageResult(page_nr=1, rank_nr=25)

    with (
        patch.object(req, "get_max_page", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_page_job(req, start_rank=25, end_rank=-1, max_page_req=mock_max_page_req)

    mock_filter.assert_awaited_once_with(max_page_req=mock_max_page_req)
    mock_extract.assert_called_once_with(start_rank=25, end_rank=-1)

    assert len(result) == 1
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 25
    assert result[0].end_rank == 25
    assert result[0].start_idx == 24
    assert result[0].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_page_job_start_rank_greater_than_end_rank_returns_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_max_page_req = MagicMock()
    mock_max_page_req.account_type = HSAccountTypes.regular
    res = GetMaxHighscorePageResult(page_nr=2, rank_nr=50)

    with (
        patch.object(req, "get_max_page", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(3, -1)) as mock_extract
    ):

        result = await get_hs_page_job(req, start_rank=51, end_rank=-1, max_page_req=mock_max_page_req)

    mock_filter.assert_awaited_once_with(max_page_req=mock_max_page_req)
    mock_extract.assert_called_once_with(start_rank=51, end_rank=-1)

    assert result == []


@pytest.mark.asyncio
async def test_get_hs_filtered_job(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.account_type = HSAccountTypes.regular
    res = GetFilteredPageRangeResult(
        start_rank=1, end_rank=50, start_page=1, end_page=2)

    with (
        patch.object(req, "get_filtered_page_range", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_filtered_job(req, start_rank=1, end_rank=-1, page_range_req=mock_page_req)

    mock_filter.assert_awaited_once_with(page_range_req=mock_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=-1)

    assert len(result) == 2
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25

    assert result[1].account_type == HSAccountTypes.regular
    assert result[1].priority == 2
    assert result[1].page_num == 2
    assert result[1].start_rank == 26
    assert result[1].end_rank == 50
    assert result[1].start_idx == 0
    assert result[1].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_filtered_job_end_rank_given(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.account_type = HSAccountTypes.regular
    res = GetFilteredPageRangeResult(
        start_rank=1, end_rank=50, start_page=1, end_page=2)

    with (
        patch.object(req, "get_filtered_page_range", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, 1)) as mock_extract
    ):

        result = await get_hs_filtered_job(req, start_rank=1, end_rank=25, page_range_req=mock_page_req)

    mock_filter.assert_awaited_once_with(page_range_req=mock_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=25)

    assert len(result) == 1
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_filtered_job_start_rank_adjusted(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.account_type = HSAccountTypes.regular
    res = GetFilteredPageRangeResult(
        start_rank=2, end_rank=50, start_page=1, end_page=2)

    with (
        patch.object(req, "get_filtered_page_range", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_filtered_job(req, start_rank=1, end_rank=-1, page_range_req=mock_page_req)

    mock_filter.assert_awaited_once_with(page_range_req=mock_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=-1)

    assert len(result) == 2
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 2
    assert result[0].end_rank == 25
    assert result[0].start_idx == 1
    assert result[0].end_idx == 25

    assert result[1].account_type == HSAccountTypes.regular
    assert result[1].priority == 2
    assert result[1].page_num == 2
    assert result[1].start_rank == 26
    assert result[1].end_rank == 50
    assert result[1].start_idx == 0
    assert result[1].end_idx == 25


@pytest.mark.asyncio
async def test_get_hs_filtered_job_end_rank_adjusted(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.account_type = HSAccountTypes.regular
    res = GetFilteredPageRangeResult(
        start_rank=1, end_rank=40, start_page=1, end_page=2)

    with (
        patch.object(req, "get_filtered_page_range", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, 2)) as mock_extract
    ):

        result = await get_hs_filtered_job(req, start_rank=1, end_rank=50, page_range_req=mock_page_req)

    mock_filter.assert_awaited_once_with(page_range_req=mock_page_req)
    mock_extract.assert_called_once_with(start_rank=1, end_rank=50)

    assert len(result) == 2
    assert result[0].account_type == HSAccountTypes.regular
    assert result[0].priority == 1
    assert result[0].page_num == 1
    assert result[0].start_rank == 1
    assert result[0].end_rank == 25
    assert result[0].start_idx == 0
    assert result[0].end_idx == 25

    assert result[1].account_type == HSAccountTypes.regular
    assert result[1].priority == 2
    assert result[1].page_num == 2
    assert result[1].start_rank == 26
    assert result[1].end_rank == 40
    assert result[1].start_idx == 0
    assert result[1].end_idx == 15


@pytest.mark.asyncio
async def test_get_hs_filtered_job_start_rank_greater_than_end_rank_returns_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.account_type = HSAccountTypes.regular
    res = GetFilteredPageRangeResult(
        start_rank=2, end_rank=2, start_page=1, end_page=1)

    with (
        patch.object(req, "get_filtered_page_range", new=AsyncMock(return_value=res)) as mock_filter,
        patch("osrs_hiscore_scrape.job.job_builder._extract_page_nr_from_rank", return_value=(1, -1)) as mock_extract
    ):

        result = await get_hs_filtered_job(req, start_rank=3, end_rank=-1, page_range_req=mock_page_req)

    mock_filter.assert_awaited_once_with(page_range_req=mock_page_req)
    mock_extract.assert_called_once_with(start_rank=3, end_rank=-1)

    assert result == []


def test_extract_page_nr_valid_cases():
    assert _extract_page_nr_from_rank(1, 25) == (1, 1)
    assert _extract_page_nr_from_rank(1, 50) == (1, 2)
    assert _extract_page_nr_from_rank(26, 50) == (2, 2)
    assert _extract_page_nr_from_rank(51, 75) == (3, 3)


def test_extract_page_nr_invalid_cases():
    with pytest.raises(ValueError, match="Start rank is smaller than 1"):
        _extract_page_nr_from_rank(0, 10)

    with pytest.raises(ValueError, match="Start rank is greater than end rank"):
        _extract_page_nr_from_rank(10, 5)
