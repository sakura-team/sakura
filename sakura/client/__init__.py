from sakura.client import apitools
from sakura.common.errors import APIReturningError
import sys, atexit

# avoid a full traceback in case of APIReturningError
saved_excepthook = sys.excepthook
def quiet_excepthook(t, value, traceback):
    if issubclass(t, APIReturningError):
        print('ERROR: ' + str(value))
    else:
        saved_excepthook(t, value, traceback)
sys.excepthook = quiet_excepthook

api = apitools.get_api()
atexit.register(api._close)
