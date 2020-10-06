from gevent.queue import Queue, Empty
from heapq import heappush, heappop
from time import time
from sakura.common.tools import ObservableEvent

# if no requests after this number of seconds, forget this listener.
LISTENER_GRACE_TIME = 120

class EventSourceMixin:
    # use properties to avoid the need to have __init__() called
    # in subclasses
    @property
    def _esm_listener_info(self):
        if not hasattr(self, '_esm_internal_listener_info'):
            self._esm_internal_listener_info = {}
        return self._esm_internal_listener_info
    @property
    def _esm_listener_timeouts(self):
        if not hasattr(self, '_esm_internal_listener_timeouts'):
            self._esm_internal_listener_timeouts = []
        return self._esm_internal_listener_timeouts
    @property
    def all_events(self):
        if not hasattr(self, '_esm_internal_all_events'):
            self._esm_internal_all_events = ObservableEvent()
        return self._esm_internal_all_events
    @property
    def on_listener_cleanup(self):
        if not hasattr(self, '_esm_internal_on_listener_cleanup'):
            self._esm_internal_on_listener_cleanup = ObservableEvent()
        return self._esm_internal_on_listener_cleanup
    def next_event(self, listener_id, timeout):
        events = self.next_events(listener_id, timeout, max_events=1)
        if len(events) == 0:
            return None
        else:
            return events[0]
    def next_events(self, listener_id, timeout, max_events=None):
        # retrieve or create listener queue
        if listener_id in self._esm_listener_info:
            queue, old_listener_timeout = self._esm_listener_info[listener_id]
            # remove old listener timeout
            self._esm_listener_timeouts.remove((old_listener_timeout, listener_id))
        else:
            queue = Queue()
        # record new listener timeout
        listener_timeout = time() + LISTENER_GRACE_TIME
        self._esm_listener_info[listener_id] = (queue, listener_timeout)
        heappush(self._esm_listener_timeouts, (listener_timeout, listener_id))
        # cleanup
        self._esm_cleanup()
        # if some events were queued, just return them
        events = []
        while not queue.empty() and (max_events is None or len(events) < max_events):
            events.append(queue.get())
        if len(events) == 1:
            return events
        elif len(events) > 1:
            return self.aggregate_events(events)
        # no events were already queued, we have to wait
        try:
            return [ queue.get(timeout=timeout) ]   # single event
        except Empty:
            return []                               # no event
    def aggregate_events(self, events):
        return events   # no aggregation, override in subclass if needed
    def _esm_cleanup(self):
        # cleanup obsolete listeners info
        curr_time = time()
        while len(self._esm_listener_timeouts) > 0 and self._esm_listener_timeouts[0][0] < curr_time:
            listener_timeout, listener_id = heappop(self._esm_listener_timeouts)
            self.on_listener_cleanup.notify(listener_id)
            del self._esm_listener_info[listener_id]
    def push_event(self, *args, **kwargs):
        # publish to subscribers of self.all_events
        self.all_events.notify(*args, **kwargs)
        # cleanup
        self._esm_cleanup()
        # publish to remaining listener queues
        for queue, listener_timeout in self._esm_listener_info.values():
            queue.put((args, kwargs))

class EventsAggregator:
    def __init__(self):
        self.esm = EventSourceMixin()
        self.monitored = {}
        self.esm.on_listener_cleanup.subscribe(self.on_listener_cleanup)
    def on_listener_cleanup(self, listener_id):
        for obj_id, info in tuple(self.monitored.items()):
            info['listeners'].discard(listener_id)
            if len(info['listeners']) == 0:
                info['obj_events'].unsubscribe(info['callback'])
            del self.monitored[obj_id]
    def monitor(self, listener_id, obj_events, obj_id):
        if obj_id not in self.monitored:
            def cb(evt_name, *args, **kwargs):
                self.on_event(obj_id, evt_name, *args, **kwargs)
            obj_events.subscribe(cb)
            self.monitored[obj_id] = {
                'listeners': set([listener_id]),
                'obj_events': obj_events,
                'callback': cb
            }
        else:
            self.monitored[obj_id]['listeners'].add(listener_id)
    def unmonitor(self, listener_id, obj_id):
        info = self.monitored[obj_id]
        info['listeners'].remove(listener_id)
        if len(info['listeners']) == 0:
            info['obj_events'].unsubscribe(info['callback'])
            del self.monitored[obj_id]
    def on_event(self, obj_id, evt_name, *args, **kwargs):
        self.esm.push_event(obj_id, evt_name, *args, **kwargs)
    def is_monitored(self, listener_id, event):
        obj_id = event[0][0]
        return obj_id in self.monitored and \
               listener_id in self.monitored[obj_id]['listeners']
    def next_events(self, listener_id, timeout, max_events=None):
        deadline = time() + timeout
        while True:
            timeout = deadline - time()
            if (timeout < 0):
                return []
            events = self.esm.next_events(listener_id, timeout, max_events=max_events)
            events = [ event for event in events if self.is_monitored(listener_id, event) ]
            if len(events) > 0:
                return events
