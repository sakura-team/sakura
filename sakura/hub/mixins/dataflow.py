import time
from sakura.hub.context import get_context
from sakura.hub.access import ACCESS_SCOPES, \
                              get_grant_level_generic, FilteredView

class DataflowMixin:
    def pack(self):
        result = dict(
            dataflow_id = self.id,
            access_scope = ACCESS_SCOPES(self.access_scope).name,
            owner = self.owner.login,
            users_rw = tuple(u.login for u in self.users_rw),
            users_ro = tuple(u.login for u in self.users_ro),
            grant_level = self.get_grant_level().name
        )
        result.update(**self.metadata)
        return result
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        # add operator instances
        result['op_instances'] = tuple(op.pack() for op in self.op_instances)
        return result
    def update_attributes(self,
                users = None, access_scope = None, owner = None,
                **metadata):
        context = get_context()
        # update users
        if users is not None:
            self.users_rw = context.users.from_logins(
                        u for u, grants in users.items() if grants['WRITE'])
            self.users_ro = context.users.from_logins(
                        u for u, grants in users.items() if grants['READ'])
        # update access scope
        if access_scope is not None:
            self.access_scope = getattr(ACCESS_SCOPES, access_scope).value
        # update metadata
        self.metadata.update(**metadata)
        # update owner
        if owner is not None:
            self.owner = context.users.get(login = owner)
    @classmethod
    def create_dataflow(cls,    name,
                                access_scope = None,
                                creation_date = None,
                                tags = (),
                                **metadata):
        context = get_context()
        if creation_date is None:
            creation_date = time.time()
        # if access_scope not specified, default to private
        if access_scope is None:
            access_scope = 'private'
        dataflow = cls( access_scope = getattr(ACCESS_SCOPES, access_scope).value,
                        owner = context.session.user.login)
        dataflow.update_attributes(
            name = name,
            creation_date = creation_date,
            tags = tags,
            **metadata
        )
        # return dataflow id
        context.db.commit()
        return dataflow.id
    def create_operator_instance(self, cls_id):
        return get_context().op_instances.create_instance(self, cls_id)
    @classmethod
    def filter_for_web_user(cls):
        return FilteredView(cls)
    def get_grant_level(self):
        return get_grant_level_generic(self)
