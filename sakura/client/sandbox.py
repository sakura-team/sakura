#!/usr/bin/env python3
import sys, pathlib, uuid, gevent, signal, atexit
from sakura.common.tools import yield_operator_subdirs
from sakura.common.streams import enable_standard_streams_redirection, LOCAL_STREAMS
from sakura.client import api, conf

def usage_and_exit():
    print('Usage: %s [<code-directory>]' % sys.argv[0])
    sys.exit(1)

def signal_handler(signal, frame):
    print()
    print('Ending sandbox.')
    sys.exit(0)

def failsafe_unregister(op_cls):
    if api.is_connected():
        op_cls.unregister()

def run():
    if len(sys.argv) < 2:
        sandbox_dir = '.'
    else:
        sandbox_dir = sys.argv[1]
    sandbox_dir = pathlib.Path(sandbox_dir)
    if not sandbox_dir.is_dir():
        usage_and_exit()
    signal.signal(signal.SIGINT, signal_handler)
    sandbox_uuid = str(uuid.uuid4())
    sandbox_dir = sandbox_dir.resolve()
    sandbox_streams = LOCAL_STREAMS
    op_dirs = list(yield_operator_subdirs(sandbox_dir))
    if len(op_dirs) == 0:
        print('Did not find sakura operator source code in this directory. Giving up.', file=sys.stderr)
        sys.exit(1)
    api.check()   # force loading conf now (if ever we need user interaction)
    if 'developer' not in api.users.current().privileges.assigned:
        print("You need a 'developer' privilege to be able to use this tool.")
        if 'developer' in api.users.current().privileges.requested:
            print("Your request was not accepted yet. Please be patient.")
            return
        else:
            answer = ""
            while answer not in ('yes', 'no'):
                answer = input("Do you want to send a request to sakura admins for this privilege? [yes|no] ").strip()
            if answer == 'no':
                return
            api.users.current().privileges.request('developer')
            print('A request was sent. Please be patient.')
            return
    enable_standard_streams_redirection()
    for op_dir in op_dirs:
        op_subdir = str(op_dir.relative_to(sandbox_dir))
        op_cls = api.op_classes.register_from_sandbox(
            sandbox_uuid, sandbox_dir, sandbox_streams, op_subdir
        )
        atexit.register(failsafe_unregister, op_cls)
        print('Exposing operator class at ' + str(op_dir))
    gevent.get_hub().join()

if __name__ == '__main__':
    run()
