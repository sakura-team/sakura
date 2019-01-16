from pathlib import Path
from sakura.common.tools import run_cmd
from sakura.common.cache import cache_result

def get_git_code_ref(code_ref):
    return code_ref.replace('branch:', 'origin/').replace('tag:', '').replace('commit:', '')

def get_git_commit_hash(code_dir, code_ref):
    if code_ref.startswith('commit:'):
        return code_ref[7:]
    else:
        return get_commit_metadata(code_dir, code_ref)['commit_hash']

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
        run_cmd('git clone --no-checkout %(url)s %(dest)s' % dict(
                    url = code_url,
                    dest = code_repodir))
    elif update:
        run_cmd('git fetch origin %(code_ref)s' % dict(
                    code_ref = code_ref.split(':')[1]), cwd=code_repodir)
    commit_hash = get_git_commit_hash(code_repodir, code_ref)
    # get worktree if needed
    worktree_dir = code_workdir / 'worktrees' / code_url_path / commit_hash
    if not worktree_dir.exists():
        worktree_dir.parent.mkdir(parents=True, exist_ok=True)
        run_cmd('git worktree add %(wtdir)s %(code_ref)s' % dict(
                    wtdir = worktree_dir,
                    code_ref = git_code_ref), cwd=code_repodir)
    return worktree_dir

def get_commit_metadata(worktree_dir, code_ref=None):
    cmd = "git log -1 --format='%H%n%at%n%ct%n%ae%n%s'"
    if code_ref != None:
        cmd += ' ' + get_git_code_ref(code_ref)
    info_lines = run_cmd(cmd, cwd=worktree_dir).splitlines()
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
    ref_name = code_ref.split(':')[1]
    # refresh our knownledge about code_ref on remote repo
    run_cmd("git fetch origin " + ref_name, cwd=worktree_dir)
    # compare commit_hash of our code vs the one of remote repo
    local_hash = get_commit_metadata(worktree_dir)['commit_hash']
    remote_hash = get_commit_metadata(worktree_dir, code_ref)['commit_hash']
    return local_hash != remote_hash

def list_remote_code_refs(code_url):
    info_tags = run_cmd("git ls-remote --tags %(url)s" % dict(url = code_url))
    tags = tuple('tag:' + line.split('/')[-1] for line in info_tags.splitlines())
    info_branches = run_cmd("git ls-remote --heads %(url)s" % dict(url = code_url))
    branches = tuple('branch:' + line.split('/')[-1] for line in info_branches.splitlines())
    return tags + branches
