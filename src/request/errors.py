class RequestFailed(Exception):
    """ Raised when an HTTP request fails. """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class IsRateLimited(Exception):
    """ Raised when data for a request responds with rate limit message. """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class NotFound(Exception):
    """ Raised when data for a request does not exist. (404) """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class ParsingFailed(Exception):
    """ Raised when data from a request cannot be parsed into the right format. """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class RetryFailed(Exception):
    """ Raised when method/coroutine reaches . """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class ServerBusy(Exception):
    """ Raised when the server is too busy to process a request (timeouts). """

    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)
