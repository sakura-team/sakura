from sakura.daemon.processing.db import drivers
from sakura.daemon.processing.db.probe import DataStoreProber

class DataStore:
    def __init__(self, host, admin_user, admin_password, driver_label):
        self.host = host
        self.admin = dict(user = admin_user, password = admin_password)
        self.driver_label = driver_label
        self.driver = drivers.get(driver_label)
        self.datasets = None    # not probed yet
    def refresh_datasets(self):
        prober = DataStoreProber(self)
        self.datasets = prober.probe()
    def get_info_serializable(self):
        datasets_desc = list(
            dataset.get_info_serializable() for dataset in self.datasets
        )
        return dict(
            host = self.host,
            driver_label = self.driver_label,
            datasets = datasets_desc
        )

