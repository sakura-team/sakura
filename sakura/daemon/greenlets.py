from sakura.common.tools import FAST_PICKLE as pickle
from gevent import Greenlet
from sakura.common.io import APIEndpoint
from sakura.daemon.tools import connect_to_hub

class HubRPCGreenlet:
    def __init__(self, engine):
        self.engine = engine
    def spawn(self):
        return Greenlet.spawn(self.run)
    def prepare(self):
        sock_file = connect_to_hub()
        pickle.dump(self.engine.name, sock_file)
        sock_file.flush()
        # handle this RPC API
        self.endpoint = APIEndpoint(
                sock_file, pickle, self.engine)
        self.engine.register_hub_api(self.endpoint.proxy)
    def run(self):
        self.endpoint.loop()
