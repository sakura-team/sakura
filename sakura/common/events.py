from gevent.queue import Queue, Empty
from heapq import heappush, heappop
from time import time

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
        if len(events) > 0:
            return events
        # no events were already queued, we have to wait
        try:
            return [ queue.get(timeout=timeout) ]   # single event
        except Empty:
            return []                               # no event
    def _esm_cleanup(self):
        # cleanup obsolete listeners info
        if len(self._esm_listener_timeouts) == 0:
            return  # no-one is listening
        curr_time = time()
        while self._esm_listener_timeouts[0][0] < curr_time:
            listener_timeout, listener_id = heappop(self._esm_listener_timeouts)
            del self._esm_listener_info[listener_id]
    def push_event(self, evt, *args, **kwargs):
        # cleanup
        self._esm_cleanup()
        # publish to remaining listener queues
        for queue, listener_timeout in self._esm_listener_info.values():
            queue.put((evt, args, kwargs))

