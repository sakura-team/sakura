from sakura.daemon.tools import load_all_in_dir

ADAPTERS = {}

def get(adapter_name):
    return ADAPTERS.get(adapter_name, None)

for module in load_all_in_dir(__name__):
    adapter_cls = module.ADAPTER
    ADAPTERS[adapter_cls.NAME] = adapter_cls

