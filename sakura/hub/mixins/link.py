
class LinkMixin:
    @property
    def dst_daemon_api(self):
        return self.dst_op.op_class.daemon.api
    @property
    def link_args(self):
        return (self.src_op.id, self.src_out_id, self.dst_op.id, self.dst_in_id)
    def pack(self):
        return dict(
            link_id = self.id,
            src_id = self.src_op.id,
            src_out_id = self.src_out_id,
            dst_id = self.dst_op.id,
            dst_in_id = self.dst_in_id,
            gui_data = self.gui_data
        )
    def link_on_daemon(self):
        self.dst_daemon_api.connect_operators(*self.link_args)
    def unlink_on_daemon(self):
        self.dst_daemon_api.disconnect_operators(*self.link_args)
    @classmethod
    def create_link(cls, src_op, src_out_id, dst_op, dst_in_id):
        # create in local db
        link = cls( src_op = src_op,
                    src_out_id = src_out_id,
                    dst_op = dst_op,
                    dst_in_id = dst_in_id)
        # link remotely
        link.link_on_daemon()
        return link
    def delete_link(self):
        self.unlink_on_daemon() # remotely
        self.delete()           # in local db
    @classmethod
    def get_possible_links(cls, src_op, dst_op):
        # list possible new links
        possible_links = dst_op.op_class.daemon.api.get_possible_links(
                                src_op.id, dst_op.id)
        # add existing links
        for l in src_op.downlinks:
            if l.dst_op.id == dst_op.id:
                possible_links += ((l.src_out_id, l.dst_in_id),)
        return possible_links
