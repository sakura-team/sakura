from gevent.socket import create_connection, IPPROTO_TCP, TCP_NODELAY
from pathlib import Path
from sakura.daemon.code.importer import pathlib_import
import sys, importlib, sakura.daemon.conf as conf
from sakura.common.io.serializer import Serializer

# contextlib.nullcontext does not exist before python 3.7
class NullContext:
    def __enter__(self):
        return None
    def __exit__(self, *exc_info):
        pass

def connect_to_hub():
    sock = create_connection((conf.hub_host, conf.hub_port))
    sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    sock_file = sock.makefile(mode='rwb', buffering=0)
    return Serializer(sock_file)

def iter_load_all_in_dir(package_name, exc_handler):
    package = sys.modules[package_name]
    if exc_handler is None:
        exc_lookup = ()
    else:
        exc_lookup = BaseException
    if hasattr(package, '__finder__'):
        # comes from our custom import system
        cm = package.__finder__
        package_dir = package.__module_path__.parent
    else:
        cm = NullContext()
        package_dir = Path(package.__path__[0])
    for modfile in package_dir.glob('*.py'):
        if str(modfile.name) == '__init__.py':
            continue
        modname = str(modfile.stem)
        try:
            with cm:
                yield importlib.import_module('.' + modname, package_name)
        except exc_lookup as exc:
            if not exc_handler(modname, exc):
                break

def load_all_in_dir(target_dir, sort = None, exc_handler = None):
    modules = list(iter_load_all_in_dir(target_dir, exc_handler))
    if sort is not None:
        modules.sort(key = sort)
    return modules
