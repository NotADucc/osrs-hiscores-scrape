from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientConnectionError
from yarl import URL

from src.request import request
from src.request.common import HSType
from src.request.errors import (IsRateLimited, NotFound, ParsingFailed,
                                RequestFailed, ServerBusy)
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
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "https_request", new=AsyncMock(return_value="<html>mock page</html>")) as mock_https, \
            patch("src.request.request._extract_hs_page_records", return_value=["rec1", "rec2"]) as mock_extract:

        result = await req.get_hs_page(mock_page_req)

    mock_https.assert_awaited_once_with(
        TEST_URL, {"category_type": mock_page_req.hs_type.get_category_value(), "table": mock_page_req.hs_type.get_category(), "page": mock_page_req.page_num})

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

    mock_https.assert_awaited_once_with(
        TEST_URL, {"player": mock_player_req.username})

    csv = [line for line in sample_csv.split('\n') if line]

    expected = PlayerRecord(username="test", csv=csv, ts=sample_ts)

    assert result == expected


@pytest.mark.asyncio
async def test_get_hs_ranks(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
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
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_hs_ranks(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == []


@pytest.mark.asyncio
async def test_get_first_rank(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_first_rank(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = [record.rank for record in sample_category_records]

    assert result == expected[0]


@pytest.mark.asyncio
async def test_get_first_rank_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_first_rank(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == -1


@pytest.mark.asyncio
async def test_get_last_rank(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_last_rank(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = [record.rank for record in sample_category_records]

    assert result == expected[-1]


@pytest.mark.asyncio
async def test_get_last_rank_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_last_rank(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == -1


@pytest.mark.asyncio
async def test_get_hs_scores(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_hs_scores(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = request._extract_record_scores(
        records=sample_category_records, hs_type=mock_page_req.hs_type)

    assert result == expected


@pytest.mark.asyncio
async def test_get_hs_scores_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_hs_ranks(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == []


@pytest.mark.asyncio
async def test_get_first_score(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_first_score(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = request._extract_record_scores(
        records=sample_category_records, hs_type=mock_page_req.hs_type)

    assert result == expected[0]


@pytest.mark.asyncio
async def test_get_first_score_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_first_score(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == -1


@pytest.mark.asyncio
async def test_get_last_score(sample_fake_client_session, sample_category_records: list[CategoryRecord]):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = 1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=sample_category_records)) as mock_hs_page:
        result = await req.get_last_score(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    expected = request._extract_record_scores(
        records=sample_category_records, hs_type=mock_page_req.hs_type)

    assert result == expected[-1]

# ------------------
# None class methods
# ------------------


def test__is_rate_limited_true():
    page = "your IP has been temporarily blocked"
    assert request._is_rate_limited(page)


def test__is_rate_limited_false():
    page = "your IP has not been temporarily blocked"
    assert not request._is_rate_limited(page)


def make_page(rows_html: str) -> str:
    """Helper to wrap rows inside a valid table structure."""
    return f"""
    <html>
      <body>
        <table class="personal-hiscores__table">
          {rows_html}
        </table>
      </body>
    </html>
    """


def test_extract_single_record():
    page = make_page("""
      <tr class="personal-hiscores__row">
        <td class="right">1</td>
        <td class="left"><a>PlayerOne</a></td>
        <td class="right">1234</td>
      </tr>
    """)

    records = request._extract_hs_page_records(page)

    assert len(records) == 1
    rec = records[0]

    assert rec.rank == 1
    assert rec.username == "PlayerOne"
    assert rec.score == 1234


def test_extract_multiple_records_and_cleanup_username():
    page = make_page("""
      <tr class="personal-hiscores__row">
        <td class="right">2</td>
        <td class="left"><a>FooĀBar</a></td>
        <td class="right">2,345</td>
      </tr>
      <tr class="personal-hiscores__row">
        <td class="right">10</td>
        <td class="left"><a>Baz\xa0Qux</a></td>
        <td class="right">9,876</td>
      </tr>
    """)

    records = request._extract_hs_page_records(page)

    assert len(records) == 2

    r1, r2 = records
    assert r1.rank == 2
    assert r1.username == "Foo Bar"  # Ā replaced with space
    assert r1.score == 2345

    assert r2.rank == 10
    assert r2.username == "Baz Qux"  # \xa0 replaced with space
    assert r2.score == 9876


def test_raises_when_table_missing():
    page = "<html><body><p>No table</p></body></html>"

    with pytest.raises(ParsingFailed):
        request._extract_hs_page_records(page)


@pytest.mark.asyncio
async def test_get_last_score_empty(sample_fake_client_session):
    req = Requests(sample_fake_client_session)

    mock_page_req = MagicMock()
    mock_page_req.page_num = -1
    mock_page_req.hs_type = HSType.overall
    mock_page_req.account_type.lookup_overall.return_value = TEST_URL

    with patch.object(req, "get_hs_page", new=AsyncMock(return_value=[])) as mock_hs_page:
        result = await req.get_last_score(mock_page_req)

    mock_hs_page.assert_awaited_once_with(page_req=mock_page_req)

    assert result == -1


def test__extract_record_scores_misc(monkeypatch, sample_category_records: list[CategoryRecord]):
    called = {}

    def fake_calc_skill_level(score, show_virtual_lvl):
        called[score] = show_virtual_lvl
        return score

    monkeypatch.setattr(
        "src.request.request.calc_skill_level", fake_calc_skill_level)

    res = request._extract_record_scores(
        records=sample_category_records, hs_type=HSType.combat)

    assert res == [400, 300, 200, 100, 10]
    assert called == {}
