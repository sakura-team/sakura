#!/usr/bin/env python3
from sakura.client import api
from sakura.common.errors import APIReturningError
import sys, code, readline, os.path, atexit, rlcompleter

# avoid a full traceback in case of APIReturningError
saved_excepthook = sys.excepthook
def quiet_excepthook(t, value, traceback):
    if issubclass(t, APIReturningError):
        print('ERROR: ' + str(value))
    else:
        saved_excepthook(t, value, traceback)
sys.excepthook = quiet_excepthook

def handle_cmd_history():
    # Persistent command history.
    histfile = os.path.join(os.environ["HOME"], ".sakura-client-history")
    try:
        readline.read_history_file(histfile)
    except IOError:
        # Existing history file can't be read.
        pass
    atexit.register(readline.write_history_file, histfile)

def enable_completion(env):
    readline.set_completer(rlcompleter.Completer(env).complete)
    readline.parse_and_bind('tab:complete')

def run():
    env = dict(api = api, sys = sys)
    handle_cmd_history()
    enable_completion(env)
    # read-eval-loop
    code.interact(  banner='Entering interpreter prompt. Use "api" variable to interact with the platform.',
                    local=env)

if __name__ == '__main__':
    run()
