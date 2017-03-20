import bottle
from collections import namedtuple
from sakura.hub.opclasses import OpClassRegistry
from sakura.hub.opinstances import OpInstanceRegistry
from sakura.hub.links import LinkRegistry
from sakura.hub.storage import CentralStorage
from sakura.common.bottle import PicklableFileRequest
from sakura.common.tools import SimpleAttrContainer

class HubContext(object):
    def __init__(self):
        self.daemons = {}
        self.db = CentralStorage()
        self.op_classes = OpClassRegistry(self.db)
        self.op_instances = OpInstanceRegistry(self.db)
        self.links = LinkRegistry()
    def get_daemon_id(self, daemon_info):
        # check if we already know this daemon description
        db_row = self.db.select_unique('Daemon',
                        name = daemon_info['name'])
        if db_row != None:
            return db_row['daemon_id']
        else:
            # otherwise, insert in db and return the id
            self.db.insert('Daemon', **daemon_info)
            self.db.commit()
            return self.db.lastrowid
    def on_daemon_connect(self, daemon_info, api):
        # register daemon info and operator classes.
        daemon_id = self.get_daemon_id(daemon_info)
        daemon_info.update(daemon_id = daemon_id, api = api, connected=True)
        # note: a SimpleAttrContainer will be more handy
        daemon_info = SimpleAttrContainer(**daemon_info)
        self.daemons[daemon_id] = daemon_info
        self.op_classes.restore_daemon_state(daemon_info)
        self.op_instances.restore_daemon_state(daemon_info, self.op_classes)
        return daemon_id
    def list_daemons_serializable(self):
        for daemon in self.daemons.values():
            d = daemon._asdict()
            del d['api']
            yield d
    def list_op_classes_serializable(self):
        return [ dict(
                    id = info.cls_id,
                    name = info.name,
                    short_desc = info.short_desc,
                    daemon = self.daemons[info.daemon_id].name,
                    tags = info.tags,
                    svg = info.icon,
                ) for info in self.op_classes.list() ]
    # instanciate an operator and return the instance id
    def create_operator_instance(self, cls_id):
        cls_info = self.op_classes[cls_id]
        daemon_info = self.daemons[cls_info.daemon_id]
        return self.op_instances.create(daemon_info, cls_info)
    def delete_operator_instance(self, op_id):
        # first: delete links attached to this operator.
        # we get a copy of the set, because we will iterate over it
        # and delete its elements.
        attached_links = set(self.op_instances[op_id].attached_links)
        for link_id in attached_links:
            self.delete_link(link_id)
        # second: delete the operator itself.
        self.op_instances.delete(op_id)
    def create_link(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        src_op = self.op_instances[src_op_id]
        dst_op = self.op_instances[dst_op_id]
        return self.links.create(src_op, src_out_id, dst_op, dst_in_id)
    def delete_link(self, link_id):
        self.links.delete(link_id)
    def serve_operator_file(self, op_id, filepath):
        if op_id in self.op_instances:
            request = PicklableFileRequest(bottle.request, filepath)
            resp = self.op_instances[op_id].serve_file(request)
            if resp[0] == True:
                return bottle.HTTPResponse(*resp[1:])
            else:
                return bottle.HTTPError(*resp[1:])
        else:
            return bottle.HTTPError(404, "No such operator instance.")
    def on_daemon_disconnect(self, daemon_id):
        self.daemons[daemon_id].connected = False
    def get_project_gui_data(self, project_id):
        row = self.db.select_unique('Project',
                                    project_id = project_id)
        if row == None:
            return None
        else:
            return row['gui_data']
    def set_project_gui_data(self, project_id, gui_data):
        self.db.insert_or_update(
                'Project', 'project_id',
                project_id = project_id,
                gui_data = gui_data)
        self.db.commit()
