import time
from sakura.common.access import GRANT_LEVELS
from sakura.common.errors import APIRequestError
from sakura.hub.context import get_context
from sakura.hub.access import pack_gui_access_info, parse_gui_access_info
from sakura.hub.mixins.bases import BaseMixin

class DataflowMixin(BaseMixin):
    def pack(self):
        result = dict(
            dataflow_id = self.id,
            **self.metadata,
            **pack_gui_access_info(self)
        )
        result.update(**self.metadata)
        return result
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        if self.get_grant_level() >= GRANT_LEVELS.read:
            # add operator instances
            result['op_instances'] = tuple(op.pack() for op in self.op_instances)
            # add links
            df_links = set(l \
                    for op in self.op_instances \
                    for l in set(op.uplinks) | set(op.downlinks))
            result['links'] = tuple(link.pack() for link in df_links)
        return result
    def describe(self):
        return "'%(name)s' dataflow" % dict(
            name = self.metadata['name']
        )
    @classmethod
    def create_dataflow(cls,    creation_date = None,
                                **kwargs):
        context = get_context()
        if not context.user_is_logged_in():
            raise APIRequestError('Please log in first!')
        # set a creation_date if missing
        if creation_date is None:
            creation_date = time.time()
        # parse access info from gui
        kwargs = parse_gui_access_info(**kwargs)
        # record owner
        grants = kwargs.pop('grants', {})
        grants[context.session.user.login] = GRANT_LEVELS.own
        # instanciate dataflow
        dataflow = cls()
        # update attributes
        dataflow.update_attributes(
            creation_date = creation_date,
            grants = grants,
            **kwargs
        )
        # return dataflow id
        context.db.commit()
        return dataflow.id
    def create_operator_instance(self, cls_id):
        return get_context().op_instances.create_instance(self, cls_id)
