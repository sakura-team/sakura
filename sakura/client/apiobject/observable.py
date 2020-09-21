from sakura.common.tools import ObservableEvent
from sakura.client.apiobject.base import APIObjectBase

class APIObservableEvent(ObservableEvent, APIObjectBase):
    """Observable event"""
    def __dir__(self):
        # hide 'notify' method which should not be called by the user
        return list(attr for attr in super().__dir__() if attr != 'notify')

