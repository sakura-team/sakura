from pathlib import Path
from sakura.common.tools import yield_operator_subdirs, run_cmd
from sakura.common.errors import APIRequestError

GIT_CLONE_TIMEOUT       = 60.0      # seconds
GIT_LS_REMOTE_TIMEOUT   =  5.0      # seconds

def fetch_updates(code_dir, code_ref):
    if code_ref.startswith('branch:'):
        cmd = 'git fetch origin ' + code_ref[7:]
    elif code_ref.startswith('tag:'):
        cmd = 'git fetch origin refs/tags/' + code_ref[4:]
    elif code_ref.startswith('commit:'):
        cmd = 'git fetch origin ' + code_ref[7:]
    elif code_ref == 'all':
        cmd = 'git fetch origin --tags'     # means "fetch all, including tags"
    try:
        run_cmd(cmd, cwd=code_dir)
    except:
        raise APIRequestError('Fetching code failed. Verify given branch or tag.')

def get_repo_url_path(repo_url):
    return repo_url.replace('//', '/').replace(':', '')

def get_repodir(code_workdir, repo_url):
    repo_url_path = get_repo_url_path(repo_url)
    code_repodir = code_workdir / 'repos' / repo_url_path
    # clone if needed
    if not code_repodir.exists():
        code_repodir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_cmd('git clone --no-checkout %(url)s %(dest)s' % dict(
                    url = repo_url,
                    dest = code_repodir),
                timeout = GIT_CLONE_TIMEOUT)
        except:
            raise APIRequestError('Cloning repository failed. Verify given URL.')
    return code_repodir

def dir_to_path(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory.resolve()

def get_worktree(code_workdir, repo_url, code_ref, commit_hash):
    code_workdir = dir_to_path(code_workdir)
    # get repo dir
    code_repodir = get_repodir(code_workdir, repo_url)
    # get worktree if needed
    repo_url_path = get_repo_url_path(repo_url)
    worktree_dir = code_workdir / 'worktrees' / repo_url_path / commit_hash
    if not worktree_dir.exists():
        # ensure our local clone knows this commit
        fetch_updates(code_repodir, 'commit:' + commit_hash)
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
    worktree_dir = dir_to_path(worktree_dir)
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

# we work on the repo directory, with 'git show-ref' to get the list
# of revisions, and 'git log <ref> -- <subdir>' to check for any modifications
# about <subdir> in each <ref>.
def list_code_revisions_including_subdir(code_workdir, repo_url, ref_type, repo_subdir):
    code_workdir = dir_to_path(code_workdir)
    # get repo dir
    code_repodir = get_repodir(code_workdir, repo_url)
    # fetch
    fetch_updates(code_repodir, 'all')
    # get refs and check each one for existence of the subdir
    result = []
    for line in run_cmd("git show-ref", cwd=code_repodir).splitlines():
        sha1, ref = line.split()
        if not ref.startswith('refs/remotes') and not ref.startswith('refs/tags'):
            continue
        if ref.startswith('refs/remotes'):
            # branch
            if ref_type == 'tag':
                continue    # caller says we should only list tags, not branches
            sakura_ref = 'branch:' + ref.split('/')[-1]
            rev_tags = ('HEAD',)
        elif ref.startswith('refs/tags'):
            # tag
            if ref_type == 'branch':
                continue    # caller says we should only list branches, not tags
            sakura_ref = 'tag:' + ref.split('/')[-1]
            rev_tags = ()
        else:
            # not branch not tag
            continue
        commits = run_cmd('git log --pretty=oneline %(sha1)s -- %(subdir)s' % dict(
            sha1 = sha1,
            subdir = repo_subdir
        ), cwd=code_repodir)
        if len(commits) == 0:
            # no commits found modifying this subdir, it does not exist in this branch / tag
            continue
        # ok, append to result
        result.append((sakura_ref, sha1, rev_tags))
    return tuple(result)

def list_code_revisions(code_workdir, repo_url, ref_type = None, repo_subdir = None):
    if repo_subdir is not None:
        # this is more expensive, call this specific procedure
        return list_code_revisions_including_subdir(code_workdir, repo_url, ref_type, repo_subdir)
    if ref_type is None:
        return list_code_revisions(code_workdir, repo_url, ref_type = 'tag') + \
               list_code_revisions(code_workdir, repo_url, ref_type = 'branch')
    code_workdir = dir_to_path(code_workdir)
    if ref_type == 'tag':
        opt = '--tags'
        rev_tags = ()
    else:   # branches
        opt = '--heads'
        rev_tags = ('HEAD',)
    try:
        info = run_cmd("git ls-remote %(opt)s %(url)s" % \
                    dict(opt = opt, url = repo_url), timeout = GIT_LS_REMOTE_TIMEOUT)
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
