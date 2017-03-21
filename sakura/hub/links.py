from collections import namedtuple

LinkInfo = namedtuple('LinkInfo', ['link_id', 'src_op', 'src_out_id', 'dst_op', 'dst_in_id'])

class Link(LinkInfo):
    def get_info_serializable(self):
        return dict(
            link_id = self.link_id,
            src_id = self.src_op.op_id,
            src_out_id = self.src_out_id,
            dst_id = self.dst_op.op_id,
            dst_in_id = self.dst_in_id
        )

QUERY_LINKS_FROM_DAEMON = """
SELECT l.*
FROM    Link l,
        OpInstance op1, OpInstance op2,
        OpClass cls1, OpClass cls2
WHERE   l.src_op_id = op1.op_id AND l.dst_op_id = op2.op_id
  AND   op1.cls_id = cls1.cls_id AND op2.cls_id = cls2.cls_id
  AND   (cls1.daemon_id = %(daemon_id)d OR cls2.daemon_id = %(daemon_id)d);
"""

class LinkRegistry(object):
    def __init__(self, db):
        self.db = db
        self.info_per_link_id = {}
    def restore_daemon_state(self, daemon_info, op_instances):
        sql = QUERY_LINKS_FROM_DAEMON % dict(
                    daemon_id = daemon_info.daemon_id)
        for link_id, src_op_id, src_out_id, dst_op_id, dst_in_id in \
                self.db.execute(sql).fetchall():
            # if both operators are available, restore the link
            if src_op_id in op_instances and dst_op_id in op_instances:
                src_op = op_instances[src_op_id]
                dst_op = op_instances[dst_op_id]
                self.instanciate(link_id, src_op, src_out_id, dst_op, dst_in_id)
    def create(self, src_op, src_out_id, dst_op, dst_in_id):
        self.db.insert('Link',
                    src_op_id = src_op.op_id,
                    src_out_id = src_out_id,
                    dst_op_id = dst_op.op_id,
                    dst_in_id = dst_in_id)
        self.db.commit()
        link_id = self.db.lastrowid
        self.instanciate(link_id, src_op, src_out_id, dst_op, dst_in_id)
        return link_id
    def instanciate(self, link_id, src_op, src_out_id, dst_op, dst_in_id):
        dst_op.daemon.api.connect_operators(
                src_op.op_id, src_out_id, dst_op.op_id, dst_in_id)
        desc = Link(link_id, src_op, src_out_id, dst_op, dst_in_id)
        self.info_per_link_id[link_id] = desc
        src_op.attached_links.add(link_id)
        dst_op.attached_links.add(link_id)
    def delete(self, link_id):
        link = self.info_per_link_id[link_id]
        src_op = link.src_op
        dst_op = link.dst_op
        dst_op.daemon.api.disconnect_operators(
            src_op.op_id, link.src_out_id, dst_op.op_id, link.dst_in_id)
        del self.info_per_link_id[link_id]
        src_op.attached_links.remove(link_id)
        dst_op.attached_links.remove(link_id)
        self.db.delete('Link', link_id = link_id)
    def __getitem__(self, link_id):
        return self.info_per_link_id[link_id]
    def __iter__(self):
        # iterate over link_id values
        return self.info_per_link_id.__iter__()

