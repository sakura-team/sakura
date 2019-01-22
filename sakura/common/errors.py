class APIReturningError(ValueError):
    pass

class APIRequestError(APIReturningError):
    pass

class APIObjectDeniedError(APIRequestError):
    pass

class APIRequestErrorOfflineDaemon(APIRequestError):
    pass

class APIRequestErrorOfflineDatastore(APIRequestError):
    pass

class IOHoldException(Exception):
    pass

class APIRemoteError(APIReturningError):
    pass

class APIInvalidRequest(Exception):
    pass
