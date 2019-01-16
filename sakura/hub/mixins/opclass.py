from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError
from sakura.common.cache import cache_result

class OpClassMixin:

    def pack(self):
        return dict(
            id = self.id,
            code_url = self.code_url,
            code_ref = self.code_ref,
            code_subdir = self.code_subdir,
            **self.metadata
        )

    @property
    def static_code_ref(self):
        return 'commit:' + self.metadata['commit_metadata']['commit_hash']

    @cache_result(15)
    def is_updatable(self):
        daemon = get_context().daemons.any_connected()
        if daemon is None:
            # no daemon connected, cannot make the test.
            # respond that we cannot update.
            return False
        return daemon.api.is_op_class_updatable(self.code_url, self.static_code_ref, self.code_ref)

    def update(self):
        cls_info = OpClassMixin.fetch_on_daemons(get_context(),
                        self.code_url, self.code_ref, self.code_subdir)
        if cls_info is None:
            raise APIRequestError(
                'Cannot update operator code until at least one sakura daemon is running.')
        self.set(metadata = cls_info)
        return self.pack()

    def instanciate(self, daemon_api, op_id):
        daemon_api.create_operator_instance(
                        self.code_url,
                        self.static_code_ref,
                        self.code_subdir,
                        op_id)

    @classmethod
    def fetch_on_daemons(cls, context, code_url, code_ref, code_subdir):
        # code_ref is "branch:<branch>" or "tag:<tag>"
        op_cls_key = code_url, code_ref, code_subdir
        cls_info = None
        for daemon in context.daemons.select():
            if daemon.connected:
                static_code_ref = daemon.api.fetch_op_class(*op_cls_key, update=True)
                if cls_info is None:
                    # in order to be sure all daemons have the same commit,
                    # we will now use a static code_ref "commit:<commit>"
                    # returned by the first reachable daemon.
                    op_cls_key = code_url, static_code_ref, code_subdir
                    # and we ask this first daemon about class metadata
                    cls_info = daemon.api.get_op_class_metadata(*op_cls_key)
        return cls_info

    @classmethod
    def register(cls, context, code_url, code_ref, code_subdir):
        if cls.get(code_url = code_url,
                   code_ref = code_ref,
                   code_subdir = code_subdir) is not None:
            raise APIRequestError('This operator class is already registered!')
        cls_info = cls.fetch_on_daemons(context, code_url, code_ref, code_subdir)
        if cls_info is None:
            raise APIRequestError(
                'Cannot register an operator class until at least one sakura daemon is running.')
        # create
        op_cls = cls(   code_url = code_url,
                        code_ref = code_ref,
                        code_subdir = code_subdir,
                        metadata = cls_info)
        context.db.commit()     # get object ID from DB
        return op_cls.pack()
