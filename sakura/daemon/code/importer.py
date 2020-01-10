from importlib.abc import SourceLoader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
import sys, importlib, uuid

# Note about 'unique imports':
# We want to be able to reload the class of a sakura operator.
# But if the module path does not change, it will hit the cache
# in sys.modules.
# So, in this case (parameter make_unique of pathlib_import()),
# we add a random ID as first component of the module path. This
# component is ignored when looking for the real filesystem path.
# This mechanism also allows to avoid conflicts with built-in
# modules (e.g. 'operator').

class Finder(MetaPathFinder):

    def __init__(self, root, prefix):
        MetaPathFinder.__init__(self)
        self.root = root
        self.prefix = prefix
        self.context_depth = 0

    def find_spec(self, fullname, path, target = None):
        location = self.root
        for mod in fullname.split("."):
            if self.prefix is not None and mod == self.prefix:
                continue
            location = location / mod
        if location.is_dir():
            location = location / '__init__.py'
            return self.build_module_spec(fullname, location, True)
        location = location.with_suffix('.py')
        if location.exists():
            return self.build_module_spec(fullname, location, False)
        else:
            return None

    def build_module_spec(self, fullname, location, is_package):
        return ModuleSpec(  fullname,
                            Loader(self, location, is_package),
                            origin=str(location.relative_to(self.root)))

    def __enter__(self):
        if self.context_depth == 0:
            sys.meta_path = sys.meta_path + [ self ]
        self.context_depth += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_depth -= 1
        if self.context_depth == 0:
            sys.meta_path.remove(self)

class Loader(SourceLoader):

    def __init__(self, finder, location, is_package):
        SourceLoader.__init__(self)
        self.finder = finder
        self.is_package = is_package
        self.location = location

    def get_data(self, fullname):
        if self.location.exists():
            return self.location.read_bytes()
        else:
            return b''

    def get_filename(self, fullname):
        path = self.location
        return str(path)

    def exec_module(self, module):
        if self.is_package:
            # make it a package
            module.__path__ = []
            module.__package__ = module.__name__
        module.__module_path__ = self.location
        module.__finder__ = self.finder
        super().exec_module(module)

def pathlib_import(env_root, mod_path, make_unique, module_attributes):
    unique_prefix = None
    if make_unique:
        load_id = str(uuid.uuid4()).replace('-', '')
        unique_prefix = 'uniqueimport' + load_id
        mod_path = unique_prefix + '.' + mod_path
    with Finder(env_root, unique_prefix):
        mod = importlib.import_module(mod_path)
        for k, v in module_attributes.items():
            setattr(mod, k, v)
        return mod
