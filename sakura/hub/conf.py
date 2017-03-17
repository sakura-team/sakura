import argparse
from sakura.common.conf import merge_args_and_conf

# note: this function is called in sakura/hub/__init__.py
#       the conf object is then available at sakura.hub.conf
def load_conf():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conf-file',
                help="Specify alternate configuration file",
                type=argparse.FileType('r'),
                default='/etc/sakura/hub.conf')
    parser.add_argument('WEBAPP',
                help="Specify web app sub-directory",
                type=str,
                default='workflow')
    defaults = dict(
        work_dir = '/var/lib/sakura'
    )
    return merge_args_and_conf(parser, defaults)
