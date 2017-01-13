#!/usr/bin/env python3

import pickle
from sakura.common.io import LocalAPIHandler, \
                    APIForwarder, get_remote_api

def rpc_server_greenlet(sock_file, engine):
    # instruct the hub that we will manage this connection
    # as a RPC server (i.e. the hub should be client)
    sock_file.write(b'RPC_SERVER\n')
    sock_file.flush()
    # handle this RPC API
    local_api = engine
    handler = LocalAPIHandler(sock_file, pickle, local_api)
    handler.loop()

def rpc_client_greenlet(sock_file, engine):
    # instruct the hub that we will use this connection as
    # a RPC client (i.e. the hub should be server)
    sock_file.write(b'RPC_CLIENT\n')
    sock_file.flush()
    # this greenlet should forward API calls over
    # the connection towards the hub.
    remote_api = get_remote_api(sock_file, pickle)
    api_forwarder = APIForwarder(remote_api)
    engine.register_hub_api(api_forwarder.ap)
    api_forwarder.run()
