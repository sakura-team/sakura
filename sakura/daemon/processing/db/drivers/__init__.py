from sakura.daemon.tools import load_all_in_dir

DRIVERS = {}

def register(driver):
    DRIVERS[driver.NAME] = driver

def get(driver_name):
    return DRIVERS.get(driver_name, None)

load_all_in_dir(__name__)

