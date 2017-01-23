import argparse
from sakura.common.conf import merge_args_and_conf

# note: this function is called in sakura/daemon/__init__.py
#       the conf object is then available at sakura.daemon.conf
def load_conf():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conf-file',
                help="Specify alternate configuration file",
                type=argparse.FileType('r'),
                default='/etc/sakura/daemon.conf')
    parser.add_argument('-d', '--daemon-desc',
                help="Text line describying this sakura daemon",
                type=str)
    return merge_args_and_conf(parser)
