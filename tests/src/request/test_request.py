from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientConnectionError
from yarl import URL

from src.request.common import HSAccountTypes, HSType
from src.request.errors import (IsRateLimited, NotFound, RequestFailed,
                                ServerBusy)
from src.request.request import Requests
from src.request.results import CategoryRecord, PlayerRecord

TEST_URL = "http://test"
TEST_USER_AGENT = "test-agent"


@pytest.mark.asyncio
async def test_get_proxy(sample_fake_client_session):
    req = Requests(sample_fake_client_session, proxy_list=["proxy1", "proxy2"])
    assert req.get_proxy() == "proxy1"
    assert req.get_proxy() == "proxy2"
    assert req.get_proxy() == "proxy1"


def test_remove_cookies(sample_fake_client_session):
    req = Requests(sample_fake_client_session)
    sample_fake_client_session.cookie_jar.clear = MagicMock()
    req.remove_cookies()
    sample_fake_client_session.cookie_jar.clear.assert_called_once()


def test_get_session(sample_fake_client_session):
    req = Requests(sample_fake_client_session)
    assert req.get_session() is sample_fake_client_session


@pytest.mark.asyncio
async def test_https_request_success(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text.return_value = "ok"
    mock_resp.url = URL(TEST_URL)
    sample_fake_client_session.get.return_value.__aenter__.return_value = mock_resp

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        result = await req.https_request(TEST_URL, params={"q": "1"})

    assert result == "ok"
    mock_resp.text.assert_awaited_once()


@pytest.mark.asyncio
async def test_https_request_rate_limited(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text.return_value = "your IP has been temporarily blocked"
    mock_resp.url = URL(TEST_URL)
    sample_fake_client_session.get.return_value.__aenter__.return_value = mock_resp

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        with pytest.raises(IsRateLimited):
            await req.https_request(TEST_URL, params={})


@pytest.mark.asyncio
async def test_https_request_not_found(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_resp = AsyncMock()
    mock_resp.status = 404
    mock_resp.text.return_value = "not found"
    mock_resp.url = URL(TEST_URL)
    sample_fake_client_session.get.return_value.__aenter__.return_value = mock_resp

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        with pytest.raises(NotFound):
            await req.https_request(TEST_URL, params={})


@pytest.mark.asyncio
async def test_https_request_other_failure(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_resp = AsyncMock()
    mock_resp.status = 500
    mock_resp.reason = "Server Error"
    mock_resp.text.return_value = "error"
    mock_resp.url = URL(TEST_URL)
    sample_fake_client_session.get.return_value.__aenter__.return_value = mock_resp

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        with pytest.raises(RequestFailed):
            await req.https_request(TEST_URL, params={})


@pytest.mark.asyncio
async def test_https_request_timeout(sample_fake_client_session):
    req = Requests(sample_fake_client_session)
    sample_fake_client_session.get.side_effect = TimeoutError

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        with pytest.raises(ServerBusy):
            await req.https_request(TEST_URL, params={})


@pytest.mark.asyncio
async def test_https_request_client_connection_error(sample_fake_client_session):
    req = Requests(sample_fake_client_session)
    sample_fake_client_session.get.side_effect = ClientConnectionError(
        "conn failed")

    with patch("fake_useragent.UserAgent") as mock_ua:
        mock_ua.return_value.random = TEST_USER_AGENT
        with pytest.raises(RequestFailed):
            await req.https_request(TEST_URL, params={})


@pytest.mark.asyncio
async def test_get_hs_page(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 3
    mock_page_req.hs_type.get_category.return_value = "overall"
    mock_page_req.hs_type.get_category_value.return_value = 0
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "https_request", new=AsyncMock(return_value="<html>mock page</html>")) as mock_https, \
            patch("src.request.request._extract_hs_page_records", return_value=["rec1", "rec2"]) as mock_extract:

        result = await req.get_hs_page(mock_page_req)

    mock_https.assert_awaited_once_with(
        TEST_URL, {"category_type": "overall", "table": 0, "page": 3})

    mock_extract.assert_called_once_with("<html>mock page</html>")

    assert result == ["rec1", "rec2"]


@pytest.mark.asyncio
async def test_get_user_stats(sample_fake_client_session, sample_csv: str, sample_ts: datetime):
    req = Requests(sample_fake_client_session)

    mock_player_req = MagicMock()
    mock_player_req.username = "test"
    mock_player_req.account_type.api_csv.return_value = TEST_URL

    with patch.object(req, "https_request", new=AsyncMock(return_value=sample_csv)) as mock_https, \
            patch("datetime.datetime") as mock_datetime:

        mock_datetime.datetime.now.return_value = sample_ts
        mock_datetime.timezone.utc = timezone.utc

        result = await req.get_user_stats(mock_player_req)

    mock_https.assert_awaited_once_with(TEST_URL, {"player": "test"})

    csv = [line for line in sample_csv.split('\n') if line]

    expected = PlayerRecord(username="test", csv=csv, ts=sample_ts)

    assert result == expected


@pytest.mark.asyncio
async def test_get_hs_ranks(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type.get_category.return_value = "overall"
    mock_page_req.hs_type.get_category_value.return_value = 0
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_hs_ranks(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = [record.rank for record in sample_category_records]

    assert result == expected

@pytest.mark.asyncio
async def test_get_hs_ranks_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type.get_category.return_value = "overall"
    mock_page_req.hs_type.get_category_value.return_value = 1
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_hs_ranks(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == []