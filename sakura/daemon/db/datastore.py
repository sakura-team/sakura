from sakura.daemon.db import drivers
from sakura.daemon.db.dataset import Dataset

class DataStoreProber:
    def __init__(self, datastore):
        self.datastore = datastore
        self.driver = datastore.driver
    def probe(self):
        admin_conn = self.driver.connect(
            host = self.datastore.host,
            **self.datastore.admin)
        self.datasets = {}
        self.driver.collect_dbs(admin_conn, self)
        self.driver.collect_db_grants(admin_conn, self)
        admin_conn.close()
        # filter-out databases with no sakura user
        datasets = tuple(
                ds for ds in self.datasets.values()
                if len(ds.users) > 0)
        return datasets
    def register_db(self, db_name):
        self.datasets[db_name] = Dataset(self.datastore, db_name)
    def register_grant(self, db_user, db_name, privtype):
        if db_user.startswith('sakura_'):
            user = db_user[7:]
            self.datasets[db_name].grant(user, privtype)

class DataStore:
    def __init__(self, host, admin_user, admin_password, driver_label):
        self.host = host
        self.admin = dict(user = admin_user, password = admin_password)
        self.driver_label = driver_label
        self.driver = drivers.get(driver_label)
        self.datasets = None    # not probed yet
    def refresh_datasets(self):
        prober = DataStoreProber(self)
        self.datasets = { d.label: d for d in prober.probe() }
    def pack(self):
        datasets_overview = tuple(
            dataset.overview() for dataset in self.datasets.values()
        )
        return dict(
            host = self.host,
            driver_label = self.driver_label,
            datasets = datasets_overview
        )
    def __getitem__(self, dataset_label):
        return self.datasets[dataset_label]
