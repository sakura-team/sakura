#!/usr/bin/env python
from sakura.client import api
from pathlib import Path

SAKURA_REPO_URL = 'https://github.com/sakura-team/sakura'

# populate local db with op_classes contained in local 'operators' dir.
local_op_dirs = set(map(str, Path('operators').iterdir()))
db_op_dirs = set(op_cls.code_subdir for op_cls in api.op_classes.values())

missing_op_dirs = local_op_dirs - db_op_dirs
if len(missing_op_dirs) > 0:
    master_commit_hash = api.misc.list_code_revisions(SAKURA_REPO_URL)[0][1]
for op_dir in missing_op_dirs:
    print('Registering ' + op_dir, end='... ')
    try:
        api.op_classes.register_from_git_repo(SAKURA_REPO_URL, 'branch:master', master_commit_hash, op_dir)
    except:
        print('FAILED. Ignored. Probably this operator does not exist in master branch.')
        continue
    print('done')
