#!/usr/bin/env python3

import pickle, gevent.pool, bisect
from gevent import Greenlet
from gevent.queue import Queue, Empty
from time import time
from sakura.common.io import LocalAPIHandler, \
                RemoteAPIForwarder, PickleLocalAPIProtocol
from sakura.daemon.tools import connect_to_hub

class DaemonGreenlet:
    def __init__(self, engine):
        self.engine = engine
    def spawn(self):
        return Greenlet.spawn(self.run)
    def write_request(self, sock_file, req):
        pickle.dump((req, self.engine.name), sock_file)
        sock_file.flush()

class RPCServerGreenlet(DaemonGreenlet):
    def prepare(self):
        sock_file = connect_to_hub()
        # instruct the hub that we will manage this connection
        # as a RPC server (i.e. the hub should be client)
        self.write_request(sock_file, b'RPC_SERVER')
        # handle this RPC API
        pool = gevent.pool.Group()
        self.handler = LocalAPIHandler(
                sock_file, PickleLocalAPIProtocol, self.engine, pool)
    def run(self):
        self.handler.loop()

class RPCClientGreenlet(DaemonGreenlet):
    def prepare(self):
        sock_file = connect_to_hub()
        # instruct the hub that we will use this connection as
        # a RPC client (i.e. the hub should be server)
        self.write_request(sock_file, b'RPC_CLIENT')
        # this greenlet should forward API calls over
        # the connection towards the hub.
        self.remote_api = RemoteAPIForwarder(sock_file, pickle)
        self.engine.register_hub_api(self.remote_api)
    def run(self):
        self.remote_api.loop()

class PlannerGreenlet:
    def __init__(self):
        self.request_queue = Queue()
        self.planned_events = []
    def plan(self, repeat_delay, event):
        self.request_queue.put((repeat_delay, event))
    def schedule(self, repeat_delay, event):
        fire_time = time() + repeat_delay
        bisect.insort(self.planned_events, (fire_time, repeat_delay, event))
    def run(self):
        while True:
            timeout = None
            if len(self.planned_events) > 0:
                fire_time = self.planned_events[0][0]
                timeout = fire_time - time()
            try:
                repeat_delay, event = self.request_queue.get(block=True, timeout=timeout)
                self.schedule(repeat_delay, event)
            except Empty:
                pass
            # run expired events
            while len(self.planned_events) > 0 and \
                    self.planned_events[0][0] < time():
                fire_time, repeat_delay, event = self.planned_events[0]
                event() # run event
                # re-schedule
                self.planned_events = self.planned_events[1:]
                self.schedule(repeat_delay, event)
    def spawn(self):
        return Greenlet.spawn(self.run)

