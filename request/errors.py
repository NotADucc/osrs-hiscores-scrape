class RequestFailed(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)


class IsRateLimited(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)


class PlayerDoesNotExist(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)


class NoProxyList(Exception):
    def __init__(self, message, details=None):
        self.details = details
        super().__init__(message)