import sys, importlib, inspect
from sakura.common.errors import APIRequestError
from sakura.daemon.processing.operator import Operator
from sakura.daemon.code.git import get_commit_metadata
from sakura.daemon.code.importer import pathlib_import

def load_op_class(worktree_dir, code_subdir, repo_type, **module_attributes):
    op_dir = worktree_dir / code_subdir
    if not op_dir.exists():
        raise APIRequestError('Operator sub-directory specified was not found in this repository.')
    if not op_dir.is_dir():
        raise APIRequestError('Path specified for "operator sub-directory" is not a directory.')
    op_py = op_dir / 'operator.py'
    if not op_py.exists():
        raise APIRequestError('No operator.py was found.')
    if not (op_dir / 'icon.svg').exists():
        raise APIRequestError('No icon.svg was found.')
    # load the module defined by operator.py
    operator_module_path = '.'.join(tuple(op_dir.relative_to(worktree_dir).parts) + ('operator',))
    mod = pathlib_import(worktree_dir, operator_module_path, make_unique=True, module_attributes=module_attributes)
    # look for the Operator subclass defined in this module
    def match(obj):
        return  inspect.isclass(obj) and \
                inspect.getmodule(obj) == mod and \
                issubclass(obj, Operator)
    matches = inspect.getmembers(mod, match)
    if len(matches) == 0:
        raise APIRequestError("No subclass of Operator found in %s/operator.py!" % op_dir.name)
    if len(matches) > 1:
        raise APIRequestError("Several subclasses of Operator found in %s/operator.py!" % op_dir.name)
    name, op_cls = matches[0]
    icon_path = op_dir / 'icon.svg'
    with icon_path.open() as icon_file:
        op_cls.ICON = icon_file.read()
    if repo_type == 'git':
        op_cls.COMMIT_INFO = get_commit_metadata(op_dir)
    return op_cls, op_dir
