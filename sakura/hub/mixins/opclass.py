from sakura.hub.mixins.bases import BaseMixin
from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError

class OpClassMixin(BaseMixin):
    SANDBOX_INFO = {}
    @property
    def enabled(self):
        return get_context().daemons.any_enabled() is not None
    @property
    def disabled_message(self):
        return "No sakura daemon connected."

    def pack_repo_info(self, revision_prefix='default_', include_sandbox_attrs=False):
        info = dict(
            repo_type = self.repo['type'],
            code_subdir = self.code_subdir
        )
        if self.repo['type'] == 'git':
            info.update({
                                        'repo_url': self.repo['url'],
                    (revision_prefix + 'code_ref'): self.repo['default_code_ref'],
                 (revision_prefix + 'commit_hash'): self.repo['default_commit_hash']
            })
        elif self.repo['type'] == 'sandbox':
            info.update(
                sandbox_uuid = self.repo['sandbox_uuid']
            )
            if include_sandbox_attrs:
                info.update(**self.get_sandbox_attrs())
        return info

    def pack(self):
        return dict(
            id = self.id,
            **self.metadata,
            **self.pack_repo_info(),
            **self.pack_status_info()
        )

    def check_revision_handling(self):
        if self.repo['type'] != 'git':
            raise APIRequestError('No revision handling for this operator class (%s-type)' % self.repo['type'])

    @property
    def default_revision(self):
        self.check_revision_handling()
        return self.repo['default_code_ref'], self.repo['default_commit_hash']

    def get_sandbox_attrs(self):
        info = OpClassMixin.SANDBOX_INFO[self.repo['sandbox_uuid']]
        return {
            'sandbox_dir': info['dir'],
            'sandbox_streams': info['streams']
        }

    def update_default_revision(self, code_ref, commit_hash):
        self.check_revision_handling()
        self.repo['default_code_ref'], self.repo['default_commit_hash'] = code_ref, commit_hash
        self.update_metadata()

    def update_metadata(self):
        metadata = None
        for daemon in get_context().daemons.select():
            if daemon.enabled:
                repo_info = self.pack_repo_info(revision_prefix='')
                if self.repo['type'] == 'sandbox':
                    repo_info.update(**self.get_sandbox_attrs())
                metadata = daemon.api.get_op_class_metadata(**repo_info)
                break
        if metadata is None:
            raise APIRequestError(
                'Cannot fetch operator class metadata until at least one sakura daemon is running.')
        self.set(metadata = metadata)

    @classmethod
    def register(cls, context, repo_type = 'git', repo_subdir = None,
                repo_url = None, default_code_ref = None, default_commit_hash = None,
                sandbox_uuid = None, sandbox_dir = None, sandbox_streams = None):
        if repo_subdir == None:
            raise APIRequestError('Invalid operator class registration request: repo_subdir not specified.')
        if repo_type == 'git':
            if None in (repo_url, default_code_ref, default_commit_hash):
                raise APIRequestError('Invalid operator class registration request: need repo_url, default_code_ref and default_commit_hash.')
            if any(op_cls.code_subdir == repo_subdir and op_cls.repo['type'] == 'git' and op_cls.repo['url'] == repo_url \
                        for op_cls in cls.select()):
                raise APIRequestError('This operator class is already registered!')
            repo_info = dict(type = 'git',
                             url = repo_url,
                             default_code_ref = default_code_ref,
                             default_commit_hash = default_commit_hash)
        elif repo_type == 'sandbox':
            if None in (sandbox_uuid, sandbox_dir, sandbox_streams):
                raise APIRequestError('Invalid operator class registration request: need sandbox_uuid, sandbox_dir, sandbox_streams.')
            cls.SANDBOX_INFO[sandbox_uuid] = { 'dir': sandbox_dir, 'streams': sandbox_streams }
            repo_info = dict(type = 'sandbox',
                             sandbox_uuid = sandbox_uuid)
        else:
            raise APIRequestError("Invalid request: Expected repo_type='git' or repo_type='sandbox'.")
        if context.daemons.any_enabled() is None:
            raise APIRequestError(
                'Cannot register an operator class until at least one sakura daemon is running.')
        # create
        op_cls = cls(   repo = repo_info,
                        code_subdir = repo_subdir)
        try:
            op_cls.update_metadata()
        except:
            op_cls.delete()
            raise
        context.db.commit()     # get object ID from DB
        return op_cls.pack()

    def create_instance(self, dataflow):
        context = get_context()
        revision_kwargs = {}
        if self.repo['type'] == 'git':
            # select a revision (commit hash) appropriate for this user:
            # - if he has already instanciated operators of this class, and all of them
            #   are linked to the same revision, re-use this revision
            # - otherwise use the default revision defined for this class of operators
            revisions = set()
            for op in self.op_instances:
                if op.dataflow.owner == context.user.login:
                    revisions.add((op.revision['code_ref'], op.revision['commit_hash']))
            if len(revisions) == 1:
                revision = revisions.pop()
            else:
                revision = self.default_revision
            code_ref, commit_hash = revision
            revision_kwargs = { 'revision': {
                    'code_ref': code_ref,
                    'commit_hash': commit_hash
            }}
        return context.op_instances.create_instance(
                dataflow = dataflow, op_cls_id = self.id, **revision_kwargs)

    @classmethod
    def prefetch_code(cls, api):
        commit_refs = set()
        for op_cls in cls.select():
            if op_cls.repo['type'] == 'git':
                # code of operator instances
                for op in op_cls.op_instances:
                    commit_refs.add((op_cls.repo['url'], op.revision['code_ref'], op.revision['commit_hash']))
                # default code ref of op_class
                commit_refs.add((op_cls.repo['url'], op_cls.repo['default_code_ref'], op_cls.repo['default_commit_hash']))
        # fetch all this
        if len(commit_refs) > 0:
            for ref in commit_refs:
                api.prefetch_code(*ref)
