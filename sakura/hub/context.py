import bottle
from collections import namedtuple
from sakura.hub.opclasses import OpClassRegistry
from sakura.hub.opinstances import OpInstanceRegistry
from sakura.hub.links import LinkRegistry
from sakura.common.bottle import PicklableFileRequest

class HubContext(object):
    def __init__(self):
        self.next_daemon_id = 0
        self.daemons = {}
        self.op_classes = OpClassRegistry()
        self.op_instances = OpInstanceRegistry()
        self.links = LinkRegistry()
    def get_daemon_id(self):
        daemon_id = self.next_daemon_id
        self.next_daemon_id += 1
        return daemon_id
    def register_daemon(self, daemon_id, daemon_info, api):
        # register daemon info and operator classes.
        # note: we convert daemon_info dict to namedtuple (it will be more handy)
        daemon_info.update(daemon_id = daemon_id, api = api)
        daemon_info = namedtuple('DaemonInfo', daemon_info.keys())(**daemon_info)
        self.daemons[daemon_id] = daemon_info
        for op_cls_info in daemon_info.op_classes:
            self.register_op_class(daemon_id, *op_cls_info)
    def list_daemons_serializable(self):
        for daemon in self.daemons.values():
            d = dict(daemon._asdict())
            del d['api']
            yield d
    def register_op_class(self, *args):
        self.op_classes.store(*args)
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
        cls_info = self.op_classes.get_cls_info(cls_id)
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
            return bottle.HTTPResponse(*resp)
        else:
            return bottle.HTTPError(404, "No such operator instance.")

