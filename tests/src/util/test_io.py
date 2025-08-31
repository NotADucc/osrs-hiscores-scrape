import asyncio
import datetime
import tempfile

import pytest

from src.request.results import CategoryRecord, PlayerRecord
from src.util.io import read_hs_records, read_proxies, write_record, write_records


ENCODING = "utf-8"


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
                assert next(read_in_lines).decode(encoding=ENCODING).strip() == line


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
                assert next(read_in_lines).decode(encoding=ENCODING).strip() == line

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
        proxy_file.write("\n".join(proxy for proxy in proxies).encode(encoding=ENCODING))
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

        hs_records = read_hs_records(file=file.name)
        assert next(hs_records) == data

def test_read_hs_records_valid_with_false_data():
    data = CategoryRecord(rank=-1, score=-1, username="test")
    with tempfile.NamedTemporaryFile(delete=False) as file:
        file.write(str(data).encode(encoding=ENCODING))
        file.write(b'\n')
        file.write(b'false data')
        file.flush()

        hs_records = read_hs_records(file=file.name)
        assert next(hs_records) == data
        assert next(hs_records, None) == None

def test_read_hs_records_valid_empty():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        hs_records = list(read_hs_records(file=file.name))
        assert not hs_records

def test_read_hs_records_valid_no_file():
    hs_records = list(read_hs_records(file=None)) # type: ignore
    assert not hs_records

