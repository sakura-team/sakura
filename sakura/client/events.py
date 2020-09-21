import gevent

EVENTS_GREENLET = None

class EventsGreenlet:
    def __init__(self, api):
        self.api = api
        self.subscribers = {}
    def _run(self):
        while True:
            for evt_args, evt_kwargs in self.api.events.next_events(2.0):
                obj_id = evt_args[0]
                if obj_id in self.subscribers:
                    cb = self.subscribers[obj_id]
                    cb(*evt_args[1:], **evt_kwargs)
    def spawn(self):
        gevent.spawn(self._run)
    def subscribe(self, obj_id, cb):
        if cb is None:
            del self.subscribers[obj_id]
        else:
            self.subscribers[obj_id] = cb

def set_event_callback(api, obj_id, cb):
    global EVENTS_GREENLET
    if EVENTS_GREENLET is None:
        EVENTS_GREENLET = EventsGreenlet(api)
        EVENTS_GREENLET.spawn()
    EVENTS_GREENLET.subscribe(obj_id, cb)
