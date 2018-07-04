#!/usr/bin/env python3

import pickle, gevent.pool
from gevent import Greenlet
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
