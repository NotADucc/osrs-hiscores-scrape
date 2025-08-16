class RequestFailed(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class IsRateLimited(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class NotFound(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class NoProxyList(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class ParsingFailed(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class RetryFailed(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class ServerBusy(Exception):
    def __init__(self, message: str, details=None):
        self.details = details
        super().__init__(message)


class FinishedScript(Exception):
    pass
