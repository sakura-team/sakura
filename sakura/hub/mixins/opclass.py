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
        info = dict(
            id = self.id,
            repo_type = self.repo['type'],
            code_subdir = self.code_subdir,
            **self.metadata,
            **self.pack_status_info()
        )
        if self.repo['type'] == 'git':
            info.update(
                code_url = self.repo['url'],
                default_code_ref = self.repo['default_code_ref'],
                default_commit_hash = self.repo['default_commit_hash']
            )
        return info

    @property
    def default_revision(self):
        return self.repo['default_code_ref'], self.repo['default_commit_hash']

    def update_default_revision(self, code_ref, commit_hash):
        if self.repo['type'] != 'git':
            raise APIRequestError('No revision handling for this operator class (%s-type)' % self.repo['type'])
        self.repo['default_code_ref'], self.repo['default_commit_hash'] = code_ref, commit_hash
        self.update_metadata()

    def update_metadata(self):
        op_cls_key = self.repo['url'], self.repo['default_code_ref'], self.repo['default_commit_hash'], self.code_subdir
        metadata = None
        for daemon in get_context().daemons.select():
            if daemon.enabled:
                metadata = daemon.api.get_op_class_metadata(*op_cls_key)
        if metadata is None:
            raise APIRequestError(
                'Cannot fetch operator class metadata until at least one sakura daemon is running.')
        self.set(metadata = metadata)

    @classmethod
    def register(cls, context, repo_type = 'git', repo_url = None,
                default_code_ref = None, default_commit_hash = None, repo_subdir = None):
        if repo_type not in ('git',) or \
               None in (repo_url, default_code_ref, default_commit_hash, repo_subdir):
            raise APIRequestError('Invalid operator class registration request.')
        if any(op_cls.code_subdir == repo_subdir and op_cls.repo['type'] == 'git' and op_cls.repo['url'] == repo_url \
                    for op_cls in cls.select()):
            raise APIRequestError('This operator class is already registered!')
        if context.daemons.any_enabled() is None:
            raise APIRequestError(
                'Cannot register an operator class until at least one sakura daemon is running.')
        # create
        op_cls = cls(   repo = dict(
                            type = 'git',
                            url = repo_url,
                            default_code_ref = default_code_ref,
                            default_commit_hash = default_commit_hash),
                        code_subdir = repo_subdir)
        try:
            op_cls.update_metadata()
        except:
            op_cls.delete()
            raise
        context.db.commit()     # get object ID from DB
        return op_cls.pack()
