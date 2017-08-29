from gevent.socket import create_connection
from pkg_resources import resource_filename
from pathlib import Path
from importlib import import_module
import sakura.daemon.conf as conf

def connect_to_hub():
    sock = create_connection((conf.hub_host, conf.hub_port))
    sock_file = sock.makefile(mode='rwb')
    return sock_file

def iter_load_all_in_dir(dir_path, exc_handler):
    if exc_handler is None:
        exc_lookup = ()
    else:
        exc_lookup = BaseException
    init_file = Path(resource_filename(dir_path, '__init__.py'))
    target_dir = init_file.parent
    for modfile in target_dir.glob('*.py'):
        if modfile.name == '__init__.py':
            continue
        modname = modfile.stem
        try:
            yield import_module(dir_path + '.' + modname)
        except exc_lookup as exc:
            if not exc_handler(modname, exc):
                break

def load_all_in_dir(dir_path, sort = None, exc_handler = None):
    modules = list(iter_load_all_in_dir(dir_path, exc_handler))
    if sort is not None:
        modules.sort(key = sort)
    return modules
