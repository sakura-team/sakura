import sakura.daemon.conf as conf
from sakura.daemon.processing.operator import Operator

class HubToDaemonAPI(object):
    def __init__(self, op_classes):
        self.op_classes = op_classes
    def get_daemon_info(self):
        op_classes_desc = list(
            Operator.descriptor(op_cls) for op_cls in self.op_classes
        )
        return dict(name=conf.daemon_desc,
                    ext_datasets=conf.external_datasets,
                    op_classes=op_classes_desc)
    def create_operator(self, *args, **kwargs):
        print("create operator:", args, kwargs)
