from sakura.hub.mixins.bases import BaseMixin
from sakura.hub.context import get_context

class LinkMixin(BaseMixin):
    INSTANCIATED = set()
    ENABLED = set()
    @property
    def instanciated(self):
        return self.id in LinkMixin.INSTANCIATED
    @instanciated.setter
    def instanciated(self, boolean):
        if boolean:
            if not self.instanciated:
                LinkMixin.INSTANCIATED.add(self.id)
        else:
            if self.instanciated:
                LinkMixin.INSTANCIATED.discard(self.id)
    @property
    def enabled(self):
        return self.id in LinkMixin.ENABLED
    @enabled.setter
    def enabled(self, boolean):
        if boolean:
            if not self.enabled:
                self.push_event('enabled')
                LinkMixin.ENABLED.add(self.id)
        else:
            if self.enabled:
                self.push_event('disabled')
                LinkMixin.ENABLED.discard(self.id)
    @property
    def disabled_message(self):
        if self.enabled:
            raise AttributeError
        return 'Output of source operator is not ready.'
    @property
    def dst_daemon(self):
        return self.dst_op.daemon
    @property
    def link_args(self):
        return (self.src_op.id, self.src_out_id, self.dst_op.id, self.dst_in_id)
    def pack(self):
        return dict(
            link_id = self.id,
            src_id = self.src_op.id,
            src_out_id = self.src_out_id,
            src_cls_name = self.src_op.op_class.metadata['name'],
            dst_id = self.dst_op.id,
            dst_in_id = self.dst_in_id,
            dst_cls_name = self.dst_op.op_class.metadata['name'],
            gui_data = self.gui_data,
            **self.pack_status_info()
        )
    def instanciate(self):
        if not self.instanciated:
            self.instanciated = True
            self.dst_daemon.api.connect_operators(*self.link_args)
    def deinstanciate(self):
        if self.instanciated:
            if self.dst_daemon.enabled:
                self.instanciated = False
                self.dst_daemon.api.disconnect_operators(*self.link_args)
            else:
                self.instanciated = False    # daemon is dead anyway
    def on_daemon_event(self, evt):
        if evt == 'input_now_none':
            self.enabled = False
        elif evt == 'input_no_longer_none':
            self.enabled = True
        else:
            raise Exception('Unexpected event')
    @classmethod
    def create_link(cls, src_op, src_out_id, dst_op, dst_in_id):
        # create in local db
        link = cls( src_op = src_op,
                    src_out_id = src_out_id,
                    dst_op = dst_op,
                    dst_in_id = dst_in_id)
        get_context().db.commit() # ensure link id is set
        src_op.dataflow.push_event('created_link', link.id)
        # link remotely
        link.instanciate()
        return link
    def delete_link(self):
        if self.instanciated:
            self.deinstanciate() # remotely
        self.src_op.dataflow.push_event('deleted_link', self.id)
        self.delete()           # in local db
    @classmethod
    def get_possible_links(cls, src_op, dst_op):
        # list possible new links
        possible_links = dst_op.daemon.api.get_possible_links(
                                src_op.id, dst_op.id)
        # add existing links
        for l in src_op.downlinks:
            if l.dst_op.id == dst_op.id:
                possible_links += ((l.src_out_id, l.dst_in_id),)
        return possible_links
