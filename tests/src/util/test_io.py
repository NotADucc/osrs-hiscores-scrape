import asyncio
import datetime
import sys
import tempfile

import pytest

from src.request.common import HSAccountTypes, HSType
from src.request.results import CategoryRecord, PlayerRecord
from src.util import json_wrapper
from src.util.io import (ENCODING, build_temp_file, filtered_result_formatter,
                         read_filtered_result, read_hs_records, read_proxies,
                         write_record, write_records)
from src.worker.job import HSLookupJob


@pytest.fixture(autouse=True)
def test_exits_if_stdin_not_tty(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["test_io.py"])

@pytest.mark.asyncio
async def test_write_records_valid():
    data = ["data", None, "data"]

    fake_q = asyncio.Queue()
    for rec in data:
        await fake_q.put(rec)

    with tempfile.NamedTemporaryFile(delete=False) as out_file:
        await write_records(
            in_queue=fake_q,
            out_file=out_file.name,
            format=lambda res: res,
            total=fake_q.qsize()
        )

        read_in_lines = iter(out_file.readlines())
        for line in data:
            if line:
                assert next(read_in_lines).decode(
                    encoding=ENCODING).strip() == line


@pytest.mark.asyncio
async def test_write_records_valid_multiple_writes():
    data = ["data", None, "data"]
    double_data = [*data, *data]

    fake_q = asyncio.Queue()
    for rec in double_data:
        await fake_q.put(rec)

    with tempfile.NamedTemporaryFile(delete=False) as out_file:
        await write_records(
            in_queue=fake_q,
            out_file=out_file.name,
            format=lambda res: res,
            total=fake_q.qsize() // 2
        )

        await write_records(
            in_queue=fake_q,
            out_file=out_file.name,
            format=lambda res: res,
            total=fake_q.qsize()
        )

        read_in_lines = iter(out_file.readlines())
        for line in double_data:
            if line:
                assert next(read_in_lines).decode(
                    encoding=ENCODING).strip() == line


def test_write_record_valid():
    data = "data"

    with tempfile.NamedTemporaryFile(delete=False) as out_file:
        write_record(
            out_file=out_file.name,
            data=data
        )

        read_in = out_file.read()
        assert read_in.decode(encoding=ENCODING).strip() == data


def test_write_record_valid_multiple_writes():
    data = "data"

    with tempfile.NamedTemporaryFile(delete=False) as out_file:
        write_record(
            out_file=out_file.name,
            data=data
        )

        write_record(
            out_file=out_file.name,
            data=data
        )

        read_in_lines = iter(out_file.readlines())
        assert next(read_in_lines).decode(encoding=ENCODING).strip() == data
        assert next(read_in_lines).decode(encoding=ENCODING).strip() == data


def test_read_proxies_valid():
    proxies = ["proxy1", "proxy2"]
    with tempfile.NamedTemporaryFile(delete=False) as proxy_file:
        proxy_file.write(
            "\n".join(proxy for proxy in proxies).encode(encoding=ENCODING))
        proxy_file.flush()
        proxy_files = read_proxies(proxy_file=proxy_file.name)
        assert len(proxy_files) == 2
        for idx, proxy in enumerate(proxies):
            assert proxies[idx] == proxy


def test_read_proxies_valid_empty():
    with tempfile.NamedTemporaryFile(delete=False) as proxy_file:
        proxy_files = read_proxies(proxy_file=proxy_file.name)
        assert not proxy_files


def test_read_proxies_valid_no_file():
    proxy_files = read_proxies(proxy_file=None)
    assert not proxy_files


def test_read_proxies_valid_false_file():
    proxy_files = read_proxies(proxy_file="false_file")
    assert not proxy_files


def test_read_hs_records_valid():
    data = CategoryRecord(rank=-1, score=-1, username="test")
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(str(data).encode(encoding=ENCODING))
        file.flush()

        hs_records = read_hs_records(file_path=file.name)
        assert next(hs_records) == data


def test_read_hs_records_valid_with_false_data():
    data = CategoryRecord(rank=-1, score=-1, username="test")
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(str(data).encode(encoding=ENCODING))
        file.write(b'\n')
        file.write(b'false data')
        file.flush()

        hs_records = read_hs_records(file_path=file.name)
        assert next(hs_records) == data
        assert next(hs_records, None) == None


def test_read_hs_records_valid_with_false_data_inline():
    data = CategoryRecord(rank=-1, score=-1, username="test")
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(str(data).encode(encoding=ENCODING))
        file.write(b'false data')
        file.flush()

        hs_records = read_hs_records(file_path=file.name)
        assert next(hs_records, None) == None


def test_read_hs_records_valid_empty():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        hs_records = list(read_hs_records(file_path=file.name))
        assert not hs_records


def test_read_hs_records_valid_no_file():
    hs_records = list(read_hs_records(file_path=None))  # type: ignore
    assert not hs_records


def test_read_filtered_result_valid():
    record = PlayerRecord(username="test", csv=[
                          "-1,-1,-1"], ts=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc))
    job = HSLookupJob(priority=-1, username=record.username,
                      account_type=HSAccountTypes.regular, result=record)
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(filtered_result_formatter(job).encode(encoding=ENCODING))
        file.flush()

        player_records = read_filtered_result(file_path=file.name)
        assert next(player_records) == record


def test_read_filtered_result_valid_with_false_data():
    record = PlayerRecord(username="test", csv=[
                          "-1,-1,-1"], ts=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc))
    job = HSLookupJob(priority=-1, username=record.username,
                      account_type=HSAccountTypes.regular, result=record)
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(filtered_result_formatter(job).encode(encoding=ENCODING))
        file.flush()

        player_records = read_filtered_result(file_path=file.name)
        assert next(player_records) == record
        assert next(player_records, None) == None


def test_read_filtered_result_valid_with_false_data_inline():
    record = PlayerRecord(username="test", csv=[
                          "-1,-1,-1"], ts=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc))
    job = HSLookupJob(priority=-1, username=record.username,
                      account_type=HSAccountTypes.regular, result=record)
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(filtered_result_formatter(job).encode(encoding=ENCODING))
        file.write(b'false data')
        file.flush()

        player_records = read_filtered_result(file_path=file.name)
        assert next(player_records, None) == None


def test_read_filtered_result_valid_empty():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        hs_records = list(read_filtered_result(file_path=file.name))
        assert not hs_records


def test_read_filtered_result_valid_no_file():
    hs_records = list(read_filtered_result(file_path=None))  # type: ignore
    assert not hs_records


def test_filtered_result_formatter_valid():
    record = PlayerRecord(username="test", csv=[
                          "-1,-1,-1"], ts=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc))
    job = HSLookupJob(priority=-1, username=record.username,
                      account_type=HSAccountTypes.regular, result=record)

    json = filtered_result_formatter(job)
    assert json == json_wrapper.to_json(
        {"rank": job.priority, "record": job.result.to_dict()})


def test_build_temp_file_valid():
    file_name = "test.txt"
    account_type = HSAccountTypes.regular
    hs_type = HSType.sol

    temp_file = build_temp_file(
        file_path=file_name, account_type=account_type, hs_type=hs_type)
    assert temp_file == "test.regular.sol.test_io.temp"
