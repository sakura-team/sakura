#!/usr/bin/env python3
from sakura.client import api, conf
import sys, code, readline, os.path, atexit, rlcompleter

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
    api.set_auto_reconnect()
    api.check()   # force loading conf now (if ever we need user interaction)
    env = dict(api = api, sys = sys)
    handle_cmd_history()
    enable_completion(env)
    # read-eval-loop
    code.interact(  banner='Entering interpreter prompt. Use "api" variable to interact with the platform.',
                    local=env)

if __name__ == '__main__':
    run()
