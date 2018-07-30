import sys, os, importlib, inspect
from sakura.common.access import ACCESS_SCOPES
from sakura.daemon.processing.operator import Operator
from sakura.daemon.db.datastore import DataStore
import sakura.daemon.conf as conf

def load_operator_classes():
    print('Loading operators at %s' % conf.operators_dir)
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
            with open(conf.operators_dir + '/' + op_dir + '/icon.svg', 'r') as icon_file:
                op_cls.ICON = icon_file.read()
            op_classes[op_cls.NAME] = op_cls
    sys.path = sys.path[1:]
    return op_classes

def load_datastores(engine):
    datastores = []
    for ds_conf in conf.data_stores:
        ds = DataStore(
            engine = engine,
            host = ds_conf.host,
            datastore_admin = ds_conf.datastore_admin,
            sakura_admin = ds_conf.sakura_admin,
            driver_label = ds_conf.driver,
            adapter_label = ds_conf.get('adapter', 'native'),
            access_scope = ACCESS_SCOPES.value(
                    ds_conf.get('access_scope', 'private'))
        )
        ds.refresh()
        datastores.append(ds)
    return datastores
