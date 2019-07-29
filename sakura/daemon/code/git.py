from pathlib import Path
from sakura.common.tools import run_cmd
from sakura.common.errors import APIRequestError

GIT_CLONE_TIMEOUT       = 60.0      # seconds
GIT_LS_REMOTE_TIMEOUT   =  5.0      # seconds

def fetch_updates(code_dir, code_ref):
    if code_ref.startswith('branch:'):
        remote_ref = code_ref[7:]
    elif code_ref.startswith('tag:'):
        remote_ref = 'refs/tags/' + code_ref[4:]
    try:
        run_cmd('git fetch origin %(remote_ref)s' % dict(
                remote_ref = remote_ref), cwd=code_dir)
    except:
        raise APIRequestError('Fetching code failed. Verify given branch or tag.')

def get_worktree(code_workdir, code_url, code_ref, commit_hash):
    code_workdir = Path(code_workdir)
    code_workdir.mkdir(parents=True, exist_ok=True)
    code_workdir = code_workdir.resolve()
    code_url_path = code_url.replace('//', '/').replace(':', '')
    code_repodir = code_workdir / 'repos' / code_url_path
    # clone if needed
    if not code_repodir.exists():
        code_repodir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_cmd('git clone --no-checkout %(url)s %(dest)s' % dict(
                    url = code_url,
                    dest = code_repodir),
                timeout = GIT_CLONE_TIMEOUT)
        except:
            raise APIRequestError('Cloning repository failed. Verify given URL.')
    # get worktree if needed
    worktree_dir = code_workdir / 'worktrees' / code_url_path / commit_hash
    if not worktree_dir.exists():
        # ensure our local clone knows this commit
        fetch_updates(code_repodir, code_ref)
        # create the worktree dir
        worktree_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_cmd('git worktree add %(wtdir)s %(commit_hash)s' % dict(
                    wtdir = worktree_dir,
                    commit_hash = commit_hash), cwd=code_repodir)
        except:
            raise APIRequestError('Could not checkout code. Verify given commit hash.')
    return worktree_dir

def get_commit_metadata(worktree_dir, commit_hash=None):
    cmd = "git log -1 --format='%H%n%at%n%ct%n%ae%n%s'"
    if commit_hash != None:
        cmd += ' ' + commit_hash
    try:
        info_lines = run_cmd(cmd, cwd=worktree_dir).splitlines()
    except:
        raise APIRequestError('Could not find given commit hash.')
    commit_hash, s_author_date, s_committer_date, author_email, commit_subject = info_lines
    return dict(
        commit_hash = commit_hash,
        author_date = int(s_author_date),
        committer_date = int(s_committer_date),
        author_email = author_email,
        commit_subject = commit_subject
    )

def list_code_revisions(code_url, ref_type = None):
    if ref_type is None:
        return list_code_revisions(code_url, 'tag') + list_code_revisions(code_url, 'branch')
    if ref_type == 'tag':
        opt = '--tags'
        rev_tags = ()
    else:   # branches
        opt = '--heads'
        rev_tags = ('HEAD',)
    try:
        info = run_cmd("git ls-remote %(opt)s %(url)s" % \
                    dict(opt = opt, url = code_url), timeout = GIT_LS_REMOTE_TIMEOUT)
    except:
        raise APIRequestError('Querying repository failed. Verify given URL.')
    words = info.strip().replace('\t', ' ').replace('/', ' ').replace('\n', ' ').split(' ')
    commits = words[0::4]
    refs = list(ref_type + ':' + w for w in words[3::4])
    rev_tags = [ rev_tags ] * len(commits)
    return tuple(zip(refs, commits, rev_tags))

def get_last_commit_hash(repo_url, code_ref):
    words = code_ref.split(':')
    if len(words) != 2 or words[0] not in ('branch', 'tag'):
        raise APIRequestError('Invalid code ref.')
    short_ref = words[1]
    try:
        info = run_cmd("git ls-remote %(url)s %(ref)s" % \
                    dict(url = repo_url, ref = short_ref), timeout = GIT_LS_REMOTE_TIMEOUT)
    except:
        raise APIRequestError('Querying repository failed. Verify given URL.')
    return info.split()[0]

def list_operator_subdirs(code_workdir, repo_url, code_ref):
    commit_hash = get_last_commit_hash(repo_url, code_ref)
    worktree_dir = get_worktree(code_workdir, repo_url, code_ref, commit_hash)
    return sorted(str(op_dir.relative_to(worktree_dir)) \
           for op_dir in yield_operator_subdirs(worktree_dir))

def yield_operator_subdirs(worktree_dir):
    # find all operator.py file
    for op_py_file in worktree_dir.glob('**/operator.py'):
        op_dir = op_py_file.parent
        # verify we also have the icon file
        if not (op_dir / 'icon.svg').exists():
            continue
        # ok for this one
        yield op_dir
