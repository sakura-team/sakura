class GuiToHubAPI(object):
    def __init__(self, context):
        self.context = context

    def list_daemons(self, *args, **kwargs):
        daemons = self.context.list_daemons()
        return daemons

    def list_operators_classes(self):
        return self.context.list_op_classes()

    def instantiate_operator(self, *args, **kwargs):
        id = args[0]
        return ("not yet")
