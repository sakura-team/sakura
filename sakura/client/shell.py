#!/usr/bin/env python3
from sakura.client import api, conf
from pathlib import Path
from gevent.socket import wait_read
import sys, code, readline, atexit, rlcompleter

def handle_cmd_history():
    # Persistent command history.
    histfile = str(Path.home() / ".sakura-client-history")
    try:
        readline.read_history_file(histfile)
    except IOError:
        # Existing history file can't be read.
        pass
    atexit.register(readline.write_history_file, histfile)

def enable_completion(env):
    readline.set_completer(rlcompleter.Completer(env).complete)
    readline.parse_and_bind('tab:complete')

SCRIPT_HEADER = """\
#!/usr/bin/env python3
import sys
from sakura.client import api

"""

class InteractiveConsole(code.InteractiveConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script_lines = SCRIPT_HEADER.splitlines()
    def raw_input(self, prompt=""):
        line = super().raw_input(prompt)
        self.script_lines.append(line)
        return line
    def save_script(self):
        saves_dir = Path.home() / '.sakura' / 'saves'
        saves_dir.mkdir(parents=True, exist_ok=True)
        i = 0
        while True:
            script_file = saves_dir / ('shell%d.py' % i)
            if script_file.exists():
                i += 1
                continue
            break
        script_file.write_text('\n'.join(self.script_lines) + '\n')
        script_file.chmod(0o755)    # make it executable
        print("Script was saved as file '%s'." % str(script_file))

def run():
    api.check()   # force loading conf now (if ever we need user interaction)
    env = dict(api = api, sys = sys)
    handle_cmd_history()
    enable_completion(env)
    # let other greenlets work when user has not started writing a new command.
    readline.set_pre_input_hook(lambda : wait_read(sys.stdin.fileno()))
    # read-eval-loop
    console = InteractiveConsole(locals=env)
    console.interact(banner='Entering interpreter prompt. Use "api" variable to interact with the platform.')
    console.save_script()

if __name__ == '__main__':
    run()
