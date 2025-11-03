import builtins
import sys
import types
from datetime import datetime, timezone
from unittest.mock import MagicMock

import psutil
import pytest
from aiohttp import ClientSession

from src.request.common import HSType
from src.request.results import CategoryRecord, PlayerRecord


@pytest.fixture
def sample_ts() -> datetime:
    return datetime(2023, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def sample_category_record() -> CategoryRecord:
    return CategoryRecord(rank=1, score=5000, username="PlayerOne")


@pytest.fixture
def sample_category_record_worse_rank() -> CategoryRecord:
    return CategoryRecord(rank=10, score=3000, username="PlayerTwo")


@pytest.fixture
def sample_category_records() -> list[CategoryRecord]:
    return [
        CategoryRecord(rank=1, score=400, username="test1"),
        CategoryRecord(rank=2, score=300, username="test2"),
        CategoryRecord(rank=3, score=200, username="test3"),
        CategoryRecord(rank=4, score=100, username="test4"),
        CategoryRecord(rank=5, score=10,  username="test5"),
    ]


@pytest.fixture
def sample_player_record_csv_list() -> list[str]:
    return ["1,50,101333" if hs_type.is_skill() else "1,50" for hs_type in HSType.get_csv_types()]


@pytest.fixture
def sample_player_record_csv_list_incomplete() -> list[str]:
    return ["-1,1,-1" if hs_type.is_skill() else "-1,1" for hs_type in HSType.get_csv_types()]


@pytest.fixture
def sample_csv(sample_player_record_csv_list) -> str:
    return "\n".join(sample_player_record_csv_list)


@pytest.fixture
def sample_player_record(sample_player_record_csv_list: list[str]) -> PlayerRecord:
    return PlayerRecord("TestUser", sample_player_record_csv_list, datetime(2023, 1, 1))


@pytest.fixture
def sample_player_records(sample_player_record_csv_list: list[str]) -> list[PlayerRecord]:
    return [PlayerRecord("TestUser1", sample_player_record_csv_list, datetime(2023, 1, 1)), PlayerRecord("TestUser2", sample_player_record_csv_list, datetime(2023, 1, 1))]


@pytest.fixture
def sample_player_record_incomplete(sample_player_record_csv_list_incomplete: list[str], sample_ts: datetime) -> PlayerRecord:
    return PlayerRecord("TestUser", sample_player_record_csv_list_incomplete, sample_ts)


@pytest.fixture
def sample_fake_client_session():
    return MagicMock(spec=ClientSession)


@pytest.fixture(autouse=True)
def patch_exit(monkeypatch):
    """ Prevent real sys.exit in tests """
    called = {}

    def fake_exit(code=1):
        called["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", fake_exit)
    return called


@pytest.fixture(autouse=True)
def patch_input(monkeypatch):
    """ Prevent blocking input() during tests """
    monkeypatch.setattr(builtins, "input", lambda *a, **kw: "")


@pytest.fixture
def mock_process(monkeypatch):
    def _make_process(name):
        parent = types.SimpleNamespace()
        parent.name = lambda: name
        proc = types.SimpleNamespace()
        proc.parent = lambda: parent
        monkeypatch.setattr(psutil, "Process", lambda pid: proc)
    return _make_process
