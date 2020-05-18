from sakura.hub.context import get_context
from sakura.common.errors import APIRequestError

def get_one_connected_daemon():
    context = get_context()
    daemon = context.daemons.any_enabled()
    if daemon is None:
        raise APIRequestError('Unable to proceed because no daemon is connected.')
    return daemon

def revision_as_tuple(rev):
    return rev['code_ref'], rev['commit_hash']

def list_code_revisions(repo_url, reference_cls_id = None, reference_op_id = None):
    if reference_cls_id is not None and reference_op_id is not None:
        raise APIRequestError('Cannot consider 2 references when listing code revisions!')
    daemon = get_one_connected_daemon()
    # prepare comparisons
    context = get_context()
    current_revision, current_code_ref, current_commit_hash = None, None, None
    recommended_revision, recommended_commit_hash = None, None
    code_subdir = None
    if reference_cls_id is not None:
        op_cls = context.op_classes[reference_cls_id]
        current_revision = revision_as_tuple(op_cls.default_revision)
        current_code_ref, current_commit_hash = current_revision
        code_subdir = op_cls.code_subdir
    if reference_op_id is not None:
        op = context.op_instances[reference_op_id]
        current_revision = revision_as_tuple(op.revision)
        cls_default_revision = revision_as_tuple(op.op_class.default_revision)
        if current_revision != cls_default_revision:
            recommended_revision = cls_default_revision
            recommended_commit_hash = recommended_revision[1]
        code_subdir = op.op_class.code_subdir
    # ask daemon
    tags_per_revision = {}
    for code_ref, commit_hash, tags in daemon.api.list_code_revisions(repo_url, code_subdir):
        revision = code_ref, commit_hash
        # check if we can match the top of our current branch,
        # and, if yes, then tag it 'newer'.
        if code_ref == current_code_ref and commit_hash != current_commit_hash:
            # "newer, recommended" would be a little "too much", so avoid that
            if commit_hash != recommended_commit_hash:
                tags += ('newer',)
        tags_per_revision[revision] = tags
    # if relevant, add current revision, or if daemon already returned it
    # (top of the branch) simply tag it.
    if current_revision is not None:
        tags = tags_per_revision.get(current_revision, ())
        tags += ('current',)
        tags_per_revision[current_revision] = tags
    # if relevant, add recommended revision, or if daemon already returned it
    # (top of the branch) simply tag it.
    if recommended_revision is not None:
        tags = tags_per_revision.get(recommended_revision, ())
        tags += ('recommended',)
        tags_per_revision[recommended_revision] = tags
    # sort, to get most important items first.
    def sort_key(elem):
        revision, tags = elem
        if 'current' in tags:
            return (-4, revision)
        if 'recommended' in tags:
            return (-3, revision)
        if 'newer' in tags:
            return (-2, revision)
        if 'branch:master' in revision:
            return (-1, revision)
        return (0, revision)
    sorted_revisions = []
    for revision, tags in sorted(tags_per_revision.items(), key=sort_key):
        tags_str = '(' + ', '.join(tags) + ')'
        sorted_revisions.append(revision + (tags_str,))
    return sorted_revisions

def list_operator_subdirs(repo_url, code_ref):
    daemon = get_one_connected_daemon()
    return daemon.api.list_operator_subdirs(repo_url, code_ref)
