class APIRequestError(ValueError):
    pass

class APIObjectDeniedError(APIRequestError):
    pass

class IOHoldException(Exception):
    pass
