import sys, argparse
from sakura.common.conf import merge_args_and_conf

# note: this function is called in sakura/hub/__init__.py
#       the conf object is then available at sakura.hub.conf
def load_conf():
    default_webapp_path = sys.prefix + '/sakura/web_interface'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conf-file',
                help="Specify alternate configuration file",
                type=argparse.FileType('r'),
                default='/etc/sakura/hub.conf')
    parser.add_argument('-d', '--webapp-dir',
                help="Specify web app directory",
                type=str,
                default=default_webapp_path)
    defaults = dict(
        work_dir = '/var/lib/sakura',
        mode = 'prod'
    )
    return merge_args_and_conf(parser, defaults)
