
class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context
    def list_daemons(self, *args, **kwargs):
        daemons = self.context.list_daemons()
        print "list_daemons:", args, kwargs, '->', daemons
        return dict(event='list_daemons', data=daemons)
