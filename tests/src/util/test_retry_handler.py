import tempfile

import pytest

from src.request.errors import NotFound, RetryFailed
from src.util.io import ENCODING
from src.util.retry_handler import retry


@pytest.mark.asyncio
async def test_retry():
    async def ok():
        return "done"

    result = await retry(ok)
    assert result == "done"


@pytest.mark.asyncio
async def test_retry_after_retries():
    calls = {"count": 0}

    async def sometimes_ok():
        calls["count"] += 1
        if calls["count"] < 3:
            raise Exception("fail")
        return "success"

    result = await retry(sometimes_ok, max_retries=5, initial_delay=0)
    assert result == "success"
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_retry_max_retries_exhausted():
    async def always_fail():
        raise Exception("nope")

    with tempfile.NamedTemporaryFile(delete=False) as err_file:
        with pytest.raises(RetryFailed):
            await retry(always_fail, max_retries=3, initial_delay=0, err_file=err_file.name)

        assert "always_fail" in err_file.read().decode(encoding=ENCODING)


@pytest.mark.asyncio
async def test_retry_notfound():
    async def notfound():
        raise NotFound("missing", details="something")

    with pytest.raises(NotFound):
        await retry(notfound)


@pytest.mark.asyncio
async def test_logs_and_exc_info(caplog):
    async def fail():
        raise Exception("error")

    with tempfile.NamedTemporaryFile(delete=False) as err_file:
        with pytest.raises(RetryFailed):
            await retry(fail, max_retries=1, initial_delay=0, err_file=err_file.name, exc_info=True)

    assert any("error" in m for m in caplog.messages)


@pytest.mark.asyncio
async def test_error_file_local_function():
    def local_fail(input):
        raise Exception("error")

    with tempfile.NamedTemporaryFile(delete=False) as err_file:
        with pytest.raises(RetryFailed):
            await retry(local_fail, max_retries=1, initial_delay=0, err_file=err_file.name, input=10)

        err_log = err_file.read().decode(encoding=ENCODING).strip()
        assert "error | {'input': 10},test_error_file_local_function.<locals>.local_fail" == err_log


def static_fail(input):
    raise Exception("error")


@pytest.mark.asyncio
async def test_error_file_static_function():
    with tempfile.NamedTemporaryFile(delete=False) as err_file:
        with pytest.raises(RetryFailed):
            await retry(static_fail, max_retries=1, initial_delay=0, err_file=err_file.name, input=10)

        err_log = err_file.read().decode(encoding=ENCODING).strip()
        assert "error | {'input': 10},static_fail" == err_log


class ErrorClass:
    def throw_error(self, input):
        raise Exception("error")


@pytest.mark.asyncio
async def test_error_file_class_function():
    error_class = ErrorClass()
    with tempfile.NamedTemporaryFile(delete=False) as err_file:
        with pytest.raises(RetryFailed):
            await retry(error_class.throw_error, max_retries=1, initial_delay=0, err_file=err_file.name, input=10)

        err_log = err_file.read().decode(encoding=ENCODING).strip()
        assert "error | {'input': 10},ErrorClass.throw_error" == err_log
