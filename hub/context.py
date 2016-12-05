
class HubContext(object):
    def __init__(self):
        self.next_daemon_id = 0
        self.daemons = {}
    def get_daemon_id(self):
        daemon_id = self.next_daemon_id
        self.next_daemon_id += 1
        return daemon_id
    def register_daemon(self, daemon_id, metadata):
        self.daemons[daemon_id] = metadata
    def list_daemons(self):
        return self.daemons
        
