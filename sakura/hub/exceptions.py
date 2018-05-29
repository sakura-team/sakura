class DaemonDataException(Exception):
    pass

class DaemonDataError(DaemonDataException):
    pass

class DaemonDataExceptionIgnoreObject(DaemonDataException):
    pass

class TransferAborted(Exception):
    pass
