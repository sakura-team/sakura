class OpClassRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_cls_id = {}
    def list(self):
        return self.info_per_cls_id.values()
    def __getitem__(self, cls_id):
        return self.info_per_cls_id[cls_id]
    def restore_daemon_state(self, daemon_info):
        daemon_id = daemon_info.daemon_id
        new_cls_per_name = { info.name: info \
            for info in daemon_info.op_classes}
        new_cls_names = set(new_cls_per_name)
        old_cls_per_name = { row['name'] : row \
            for row in self.db.select('OpClass', daemon_id=daemon_id)}
        old_cls_names = set(old_cls_per_name)
        # forget obsolete classes and instances from db
        for cls_name in old_cls_names - new_cls_names:
            cls_id = old_cls_per_name[cls_name]['cls_id']
            # note this will also delete related instances and so on
            # (because of ON DELETE CASCADE clause on db schema)
            self.db.delete('OpClass', cls_id=cls_id)
        # add new classes in db
        for cls_name in new_cls_names - old_cls_names:
            self.db.insert('OpClass', daemon_id=daemon_id, name=cls_name)
        # if any change was made, commit
        if len(new_cls_names ^ old_cls_names) > 0:
            self.db.commit()
        # retrieve updated info from db (because we need the class ids)
        for row in self.db.select('OpClass', daemon_id=daemon_id):
            name, cls_id = row['name'], row['cls_id']
            info = new_cls_per_name[name]
            info.daemon_id = daemon_id
            info.cls_id = cls_id
            self.info_per_cls_id[cls_id] = info
