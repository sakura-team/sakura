from sakura.common.errors import APIReturningError
import sys, atexit, socket

# avoid a full traceback in case of APIReturningError or
# connection error.
saved_excepthook = sys.excepthook
def quiet_excepthook(t, value, traceback):
    if issubclass(t, APIReturningError):
        print('ERROR: ' + str(value))
    elif issubclass(t, socket.error):
        print('ERROR: issue while connecting to sakura hub!')
    else:
        saved_excepthook(t, value, traceback)
sys.excepthook = quiet_excepthook

from sakura.client import conftools
conf = conftools.get_conf()
from sakura.client import apitools
api = apitools.get_api()
atexit.register(api._close)
