from pathlib import Path
from sakura.common.tools import run_cmd
from sakura.common.cache import cache_result
from sakura.common.errors import APIRequestError

def get_git_code_ref(code_ref):
    tokens = code_ref.split(':')
    if len(tokens) == 2:
        ref_type, ref_name = code_ref.split(':')
        if ref_type == 'branch':
            return 'origin/' + ref_name
        elif ref_type in ('tag', 'commit'):
            return ref_name
    raise APIRequestError('Invalid code ref.')

def get_git_commit_hash(code_dir, code_ref):
    if code_ref.startswith('commit:'):
        return code_ref[7:]
    else:
        return get_commit_metadata(code_dir, code_ref)['commit_hash']

def fetch_code_ref(code_dir, code_ref):
    ref_name = code_ref.split(':')[1]
    # refresh our knownledge about code_ref on remote repo
    try:
        run_cmd('git fetch origin %(code_ref)s' % dict(
                code_ref = ref_name), cwd=code_dir)
    except:
        raise APIRequestError('Fetching code failed. Verify given code-ref.')

def get_worktree(code_workdir, code_url, code_ref, update=False):
    code_workdir = Path(code_workdir)
    code_workdir.mkdir(parents=True, exist_ok=True)
    code_workdir = code_workdir.resolve()
    code_url_path = code_url.replace('//', '/').replace(':', '')
    code_repodir = code_workdir / 'repos' / code_url_path
    git_code_ref = get_git_code_ref(code_ref)
    # clone if needed
    if not code_repodir.exists():
        code_repodir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_cmd('git clone --no-checkout %(url)s %(dest)s' % dict(
                    url = code_url,
                    dest = code_repodir),
                timeout = 5.0)
        except:
            raise APIRequestError('Cloning repository failed. Verify given URL.')
    elif update:
        fetch_code_ref(code_repodir, code_ref)
    commit_hash = get_git_commit_hash(code_repodir, code_ref)
    # get worktree if needed
    worktree_dir = code_workdir / 'worktrees' / code_url_path / commit_hash
    if not worktree_dir.exists():
        worktree_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_cmd('git worktree add %(wtdir)s %(code_ref)s' % dict(
                    wtdir = worktree_dir,
                    code_ref = git_code_ref), cwd=code_repodir)
        except:
            raise APIRequestError('Could not checkout code. Verify given code-ref.')
    return worktree_dir

def get_commit_metadata(worktree_dir, code_ref=None):
    cmd = "git log -1 --format='%H%n%at%n%ct%n%ae%n%s'"
    if code_ref != None:
        cmd += ' ' + get_git_code_ref(code_ref)
    try:
        info_lines = run_cmd(cmd, cwd=worktree_dir).splitlines()
    except:
        raise APIRequestError('Could not find given code-ref.')
    commit_hash, s_author_date, s_committer_date, author_email, commit_subject = info_lines
    return dict(
        commit_hash = commit_hash,
        author_date = int(s_author_date),
        committer_date = int(s_committer_date),
        author_email = author_email,
        commit_subject = commit_subject
    )

@cache_result(15)
def is_updatable(worktree_dir, code_ref):
    fetch_code_ref(worktree_dir, code_ref)
    # compare commit_hash of our code vs the one of remote repo
    local_hash = get_commit_metadata(worktree_dir)['commit_hash']
    remote_hash = get_commit_metadata(worktree_dir, code_ref)['commit_hash']
    return local_hash != remote_hash

def list_remote_code_refs(code_url):
    try:
        info_tags = run_cmd("git ls-remote --tags %(url)s" % dict(url = code_url), timeout = 3.0)
        tags = tuple('tag:' + line.split('/')[-1] for line in info_tags.splitlines())
        info_branches = run_cmd("git ls-remote --heads %(url)s" % dict(url = code_url), timeout = 3.0)
        branches = tuple('branch:' + line.split('/')[-1] for line in info_branches.splitlines())
    except:
        raise APIRequestError('Querying repository failed. Verify given URL.')
    return tags + branches
