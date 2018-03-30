class APIRequestError(ValueError):
    pass

class APIObjectDeniedError(APIRequestError):
    pass
