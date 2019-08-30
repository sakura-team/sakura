from sakura.daemon.tools import load_all_in_dir

def failed_dataset_load(modname, exc):
    print('WARNING: could not load dataset %s: %s. IGNORED.' % \
                            (modname, str(exc).strip()))
    return True     # continue with next datasets

def load():
    # load all datasets (= modules of this datasets directory)
    # and return them.
    # preserve the same order if possible.
    return load_all_in_dir(__name__,
                           exc_handler = failed_dataset_load)
