from sakura.client import apitools
import atexit
api = apitools.get_api()
atexit.register(api._close)
