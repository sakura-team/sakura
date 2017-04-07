from pkg_resources import resource_filename
from pathlib import Path
from importlib import import_module

def iter_load():
    this_file = Path(resource_filename(__name__, '__init__.py'))
    datasets_dir = this_file.parent
    for dataset_modfile in datasets_dir.glob('*.py'):
        if dataset_modfile.name == '__init__.py':
            continue
        modname = dataset_modfile.stem
        yield import_module(__name__ + '.' + modname)

def load():
    # load all datasets (= modules of this datasets directory)
    # and return them.
    # preserve the same order if possible.
    return sorted(iter_load(), key = lambda ds: ds.NAME)

