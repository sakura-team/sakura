from sakura.common.tools import SimpleAttrContainer

QUERY_DATASETS_FROM_DAEMON = """
SELECT Dataset.*
FROM DataStore, Dataset
WHERE DataStore.datastore_id = Dataset.datastore_id
  AND DataStore.daemon_id = %d;
"""

class DatasetRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_dataset_id = {}
    def list(self):
        return tuple(self.info_per_dataset_id.values())
    def __getitem__(self, dataset_id):
        return self.info_per_dataset_id[dataset_id]
    def restore_daemon_state(self, daemon_id, datasets_info):
        new_dataset_dict = {}
        for datastore_id, datasets in datasets_info:
            for dataset in datasets:
                key = (datastore_id, dataset['label'])
                new_dataset_dict[key] = SimpleAttrContainer(**dataset)
        new_dataset_keys = set(new_dataset_dict)
        old_dataset_dict = {
            (row['datastore_id'], row['label']) : row \
            for row in self.db.execute(QUERY_DATASETS_FROM_DAEMON % daemon_id)}
        old_dataset_keys = set(old_dataset_dict)
        # forget obsolete datasets from db
        for dataset_key in old_dataset_keys - new_dataset_keys:
            dataset_id = old_dataset_dict[dataset_key]['dataset_id']
            self.db.delete('Dataset', dataset_id=dataset_id)
        # add new datasets in db
        for key in new_dataset_keys - old_dataset_keys:
            self.db.insert('Dataset', datastore_id=key[0], label=key[1])
        # if any change was made, commit
        if len(new_dataset_keys ^ old_dataset_keys) > 0:
            self.db.commit()
        # retrieve updated info from db (because we need the ids)
        for row in self.db.execute(QUERY_DATASETS_FROM_DAEMON % daemon_id):
            dataset_id, datastore_id, label = \
                row['dataset_id'], row['datastore_id'], row['label']
            self.info_per_dataset_id[dataset_id] = SimpleAttrContainer(
                datastore_id = datastore_id,
                dataset_id = dataset_id,
                label = label
            )
