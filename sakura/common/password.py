#!/usr/bin/env python3
import sys, tty, termios
from base64 import b64encode, b64decode

class PasswordInput:
    def __init__(self):
        self.tty_fd = sys.stdout.fileno()
        # save
        self.saved = termios.tcgetattr(self.tty_fd)
    def __enter__(self):
        # set raw mode
        tty.setraw(self.tty_fd, termios.TCSADRAIN)
        # disable echo
        new = termios.tcgetattr(self.tty_fd)
        new[3] &= ~termios.ECHO
        termios.tcsetattr(self.tty_fd, termios.TCSADRAIN, new)
        return self
    def print(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()
    def getpass(self, prompt):
        self.print(prompt)
        passwd = ''
        while True:
            c = sys.stdin.read(1)
            if c == '\r':
                self.print('\r\n')
                break
            passwd += c
            self.print('*')
        return passwd
    def __exit__(self, t, value, traceback):
        # return saved conf
        termios.tcsetattr(self.tty_fd, termios.TCSADRAIN, self.saved)

def prompt_for_password(prompt1 = 'Enter password to encode: ',
                        prompt2 = 'Enter same password again: '):
    while True:
        with PasswordInput() as pw_input:
            passwd = pw_input.getpass(prompt1)
            passwd_again = pw_input.getpass(prompt2)
        if passwd != passwd_again:
            print('Passwords do not match.')
            continue
        print('Thanks.')
        break
    b64_repr = b64encode(passwd.encode('utf-8'))
    return b64_repr.decode('utf-8')

def password_encoder_tool():
    encoded_password = prompt_for_password()
    print('Encoded password is: "%s"' % encoded_password)

def decode_password(encoded_pw):
    return b64decode(encoded_pw.encode('utf-8')).decode('utf-8')

USAGE = '''\
Usage:
%(prog)s prompt '<prompt1>'
'''

def main():
    if len(sys.argv) < 3 or sys.argv[1] != 'prompt':
        print(USAGE % dict(prog = sys.argv[0]))
        sys.exit()
    encoded_password = prompt_for_password(sys.argv[2])
    sys.stderr.write(encoded_password)

if __name__ == "__main__":
    main()
