import sys, importlib, inspect
from sakura.daemon.processing.operator import Operator
from sakura.daemon.code.git import get_commit_metadata

def load_op_class(op_dir):
    sys.path.insert(0, str(op_dir.parent))
    # load the module defined by operator.py
    # note: we load from parent dir to avoid conflict
    # with built-in 'operator' module.
    mod = importlib.import_module(op_dir.name + '.operator')
    # look for the Operator subclass defined in this module
    def match(obj):
        return  inspect.isclass(obj) and \
                inspect.getmodule(obj) == mod and \
                issubclass(obj, Operator)
    matches = inspect.getmembers(mod, match)
    if len(matches) == 0:
        raise Exception("No subclass of Operator found in %s/operator.py!" % op_dir.name)
    if len(matches) > 1:
        raise Exception("Several subclasses of Operator found in %s/operator.py!" % op_dir.name)
    name, op_cls = matches[0]
    icon_path = op_dir / 'icon.svg'
    with icon_path.open() as icon_file:
        op_cls.ICON = icon_file.read()
    op_cls.COMMIT_INFO = get_commit_metadata(op_dir)
    sys.path = sys.path[1:]
    return op_cls
