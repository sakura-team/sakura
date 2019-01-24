class APIReturningError(ValueError):
    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = {}
        return self._data
    @data.setter
    def data(self, value):
        self._data = value

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
