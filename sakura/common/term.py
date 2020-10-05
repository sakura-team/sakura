from functools import lru_cache
import sys, tty, termios, array, fcntl, curses, unicodedata
import numpy as np

class TTYSettings(object):
    def __init__(self):
        self.tty_fd = sys.stdout.fileno()
        # save
        self.saved = termios.tcgetattr(self.tty_fd)
        self.win_size = self.get_win_size()
        self.rows, self.cols = self.win_size[0], self.win_size[1]
        curses.setupterm()
        self.num_colors = curses.tigetnum("colors")
    def set_raw_no_echo(self):
        # set raw mode
        tty.setraw(self.tty_fd, termios.TCSADRAIN)
        # disable echo
        new = termios.tcgetattr(self.tty_fd)
        new[3] &= ~termios.ECHO
        termios.tcsetattr(self.tty_fd, termios.TCSADRAIN, new)
    def restore(self):
        # return saved conf
        termios.tcsetattr(self.tty_fd, termios.TCSADRAIN, self.saved)
    def get_win_size(self):
        buf = array.array('h', [0, 0, 0, 0])
        fcntl.ioctl(self.tty_fd, termios.TIOCGWINSZ, buf, True)
        return buf
    def enter_alt_screen_buffer(self):
        print('\x1b[?1049h')
    def leave_alt_screen_buffer(self):
        print('\x1b[?1049l')

# handle the fact some chars (such as emoticons) are displayed on the terminal
# using twice the width of a standard char (on a fixed-size font)
@lru_cache(maxsize=512)
def term_char_size(c):
    return 2 if (unicodedata.east_asian_width(c) == 'W') else 1

def term_char_widths(s):
    return (term_char_size(c) for c in s)

@lru_cache(maxsize=1024)
def term_length(s):
    return sum(term_char_widths(s))

@lru_cache(maxsize=1024)
def term_truncate(s, length, truncate_sign=''):
    if len(s) == 0:
        return 0, s
    csum = np.cumsum(np.fromiter(term_char_widths(s), dtype='int'))
    if csum[-1] <= length:
        return csum[-1], s    # fast path
    length -= len(truncate_sign)
    start_offset = len(csum) - (csum[-1] - len(csum)) - len(truncate_sign)
    offset = start_offset + np.searchsorted(csum[start_offset:], length, side='right')
    s = s[:offset] + truncate_sign
    return csum[offset-1] + len(truncate_sign), s
