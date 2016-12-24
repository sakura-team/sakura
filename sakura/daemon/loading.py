import sys, os, importlib, inspect
from sakura.daemon.processing.operator import Operator
import sakura.daemon.conf as conf

def load_operator_classes():
    op_classes = {}
    sys.path.insert(0, conf.operators_dir)
    # for each operator directory
    for op_dir in os.listdir(conf.operators_dir):
        # load the module defined by operator.py
        mod = importlib.import_module(op_dir + '.operator')
        # look for the Operator subclass defined in this module
        def match(obj):
            return  inspect.isclass(obj) and \
                    inspect.getmodule(obj) == mod and \
                    issubclass(obj, Operator)
        matches = inspect.getmembers(mod, match)
        if len(matches) == 0:
            print("warning: no subclass of Operator found in %s/operator.py. Ignoring." % op_dir)
            continue
        for name, op_cls in matches:
            op_classes[op_cls.NAME] = op_cls
    sys.path = sys.path[1:]
    print(op_classes)
    return op_classes

def init_connexion_to_hub(remote_api):
    remote_api.register_daemon(name=conf.daemon_desc)
    for ext_info in conf.external_datasets:
        remote_api.register_external_dataset(**ext_info)
