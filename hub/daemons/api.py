
class DaemonToHubAPI(object):
    def __init__(self, daemon_id, context):
        self.daemon_id = daemon_id
        self.context = context
    def register_external_dataset(self, *args, **kwargs):
        print "daemon %d:" % self.daemon_id, args, kwargs
    def register_daemon(self, **metadata):
        self.context.register_daemon(self.daemon_id, metadata)
        
