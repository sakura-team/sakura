from collections import namedtuple

LinkInfo = namedtuple('LinkInfo', ['link_id', 'src_op', 'src_out_id', 'dst_op', 'dst_in_id'])

class LinkRegistry(object):
    def __init__(self):
        self.next_link_id = 0
        self.info_per_link_id = {}
    def create(self, src_op, src_out_id, dst_op, dst_in_id):
        link_id = self.next_link_id
        self.next_link_id += 1
        dst_op.daemon.api.connect_operators(
                src_op.op_id, src_out_id, dst_op.op_id, dst_in_id)
        desc = LinkInfo(link_id, src_op, src_out_id, dst_op, dst_in_id)
        self.info_per_link_id[link_id] = desc
        src_op.attached_links.add(link_id)
        dst_op.attached_links.add(link_id)
        return link_id
    def delete(self, link_id):
        link = self.info_per_link_id[link_id]
        src_op = link.src_op
        dst_op = link.dst_op
        dst_op.daemon.api.disconnect_operators(
            src_op.op_id, link.src_out_id, dst_op.op_id, link.dst_in_id)
        del self.info_per_link_id[link_id]
        src_op.attached_links.remove(link_id)
        dst_op.attached_links.remove(link_id)
    def __getitem__(self, link_id):
        return self.info_per_link_id[link_id]

