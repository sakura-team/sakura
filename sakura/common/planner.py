#!/usr/bin/env python3
import bisect
from gevent import Greenlet
from gevent.queue import Queue, Empty
from time import time

class PlannerGreenlet:
    def __init__(self):
        self.request_queue = Queue()
        self.planned_events = []
    def plan(self, repeat_delay, event):
        self.request_queue.put((repeat_delay, event))
    def run_once(self, event):
        self.plan(None, event)
    def schedule(self, repeat_delay, event):
        fire_time = time()
        if repeat_delay is not None:
            fire_time += repeat_delay
        bisect.insort(self.planned_events, (fire_time, repeat_delay, event))
    def run(self):
        while True:
            timeout = None
            if len(self.planned_events) > 0:
                fire_time = self.planned_events[0][0]
                timeout = fire_time - time()
            try:
                # schedule event for the 1st time
                repeat_delay, event = self.request_queue.get(block=True, timeout=timeout)
                self.schedule(repeat_delay, event)
            except Empty:
                pass
            # run expired events
            while len(self.planned_events) > 0 and \
                    self.planned_events[0][0] < time():
                fire_time, repeat_delay, event = self.planned_events[0]
                event() # run event
                self.planned_events = self.planned_events[1:]
                if repeat_delay is not None:
                    # re-schedule
                    self.schedule(repeat_delay, event)
    def spawn(self):
        return Greenlet.spawn(self.run)
