import tempfile

from src.util.io import read_proxies


ENCODING = "utf-8"


def test_read_proxies_valid():
    proxies = ["proxy1", "proxy2"]
    with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False) as proxy_file:
        proxy_file.write("\n".join(proxy for proxy in proxies).encode(encoding=ENCODING))
        proxy_file.close()

        proxy_files = read_proxies(proxy_file=proxy_file.name)
        assert len(proxy_files) == 2
        for idx, proxy in enumerate(proxies):
            assert proxies[idx] == proxy


def test_read_proxies_valid_empty():
    with tempfile.NamedTemporaryFile(delete=False, delete_on_close=False) as proxy_file:
        proxy_file.close()

        proxy_files = read_proxies(proxy_file=proxy_file.name)
        assert len(proxy_files) == 0


def test_read_proxies_valid_no_file():
    proxy_files = read_proxies(proxy_file=None)
    assert len(proxy_files) == 0

def test_read_proxies_valid_false_file():
    proxy_files = read_proxies(proxy_file="false_file")
    assert len(proxy_files) == 0