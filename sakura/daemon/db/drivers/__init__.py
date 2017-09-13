from sakura.daemon.tools import load_all_in_dir

DRIVERS = {}

def get(driver_name):
    return DRIVERS.get(driver_name, None)

for module in load_all_in_dir(__name__):
    driver_cls = module.DRIVER
    DRIVERS[driver_cls.NAME] = driver_cls

