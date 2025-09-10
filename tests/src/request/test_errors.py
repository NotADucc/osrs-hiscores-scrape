import pytest

from src.request.errors import (IsRateLimited, NotFound, ParsingFailed,
                                RequestFailed, RetryFailed, ServerBusy)


@pytest.mark.parametrize(
    "exc_class",
    [
        (RequestFailed),
        (IsRateLimited),
        (NotFound),
        (ParsingFailed),
        (RetryFailed),
        (ServerBusy),
    ]
)
def test_error_without_details(exc_class):
    message = f"raise {exc_class.__name__}"

    err = exc_class(message)

    assert str(err) == message
    assert err.details is None


@pytest.mark.parametrize(
    "exc_class",
    [
        (RequestFailed),
        (IsRateLimited),
        (NotFound),
        (ParsingFailed),
        (RetryFailed),
        (ServerBusy),
    ]
)
def test_error_with_details(exc_class):
    message = f"raise {exc_class.__name__}"
    details = {"code": 123, "info": "extra"}

    err = exc_class(message, details=details)

    assert str(err) == message
    assert err.details == details


@pytest.mark.parametrize(
    "exc_class",
    [
        (RequestFailed),
        (IsRateLimited),
        (NotFound),
        (ParsingFailed),
        (RetryFailed),
        (ServerBusy),
    ]
)
def test_error_raise_and_catch(exc_class):
    message = f"raise {exc_class.__name__}"
    details = {"id": 42}

    with pytest.raises(exc_class) as e:
        raise exc_class(message, details)

    err = e.value
    assert str(err) == message
    assert err.details == details
