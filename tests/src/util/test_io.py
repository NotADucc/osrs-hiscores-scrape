import asyncio
import tempfile

import pytest

from src.util.io import read_proxies, write_record, write_records


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
        assert len(proxy_files) == 0


def test_read_proxies_valid_no_file():
    proxy_files = read_proxies(proxy_file=None)
    assert len(proxy_files) == 0


def test_read_proxies_valid_false_file():
    proxy_files = read_proxies(proxy_file="false_file")
    assert len(proxy_files) == 0