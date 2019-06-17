from sakura.hub.mixins.bases import BaseMixin
from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError

class OpClassMixin(BaseMixin):
    @property
    def enabled(self):
        return get_context().daemons.any_enabled() is not None
    @property
    def disabled_message(self):
        return "No sakura daemon connected."

    def pack(self):
        return dict(
            id = self.id,
            code_url = self.code_url,
            code_subdir = self.code_subdir,
            default_code_ref = self.default_code_ref,
            default_commit_hash = self.default_commit_hash,
            **self.metadata,
            **self.pack_status_info()
        )

    @property
    def default_revision(self):
        return self.default_code_ref, self.default_commit_hash

    def update_default_revision(self, code_ref, commit_hash):
        self.default_code_ref, self.default_commit_hash = code_ref, commit_hash
        self.update_metadata()

    def update_metadata(self):
        op_cls_key = self.code_url, self.default_code_ref, self.default_commit_hash, self.code_subdir
        metadata = None
        for daemon in get_context().daemons.select():
            if daemon.enabled:
                metadata = daemon.api.get_op_class_metadata(*op_cls_key)
        if metadata is None:
            raise APIRequestError(
                'Cannot fetch operator class metadata until at least one sakura daemon is running.')
        self.set(metadata = metadata)

    @classmethod
    def register(cls, context, code_url, default_code_ref, default_commit_hash, code_subdir):
        if cls.get(code_url = code_url,
                   code_subdir = code_subdir) is not None:
            raise APIRequestError('This operator class is already registered!')
        if context.daemons.any_enabled() is None:
            raise APIRequestError(
                'Cannot register an operator class until at least one sakura daemon is running.')
        # create
        op_cls = cls(   code_url = code_url,
                        code_subdir = code_subdir,
                        default_code_ref = default_code_ref,
                        default_commit_hash = default_commit_hash)
        try:
            op_cls.update_metadata()
        except:
            op_cls.delete()
            raise
        context.db.commit()     # get object ID from DB
        return op_cls.pack()
