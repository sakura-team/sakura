import json, sys
import argparse

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
    args_conf = parser.parse_args()
    file_conf = json.load(args_conf.conf_file)

    conf = args_conf
    del conf.conf_file
    for name, value in file_conf.items():
        name = name.replace('-', '_')
        # prefer the value specified in the command line if any
        if name not in conf or getattr(conf, name) == None:
            setattr(conf, name, value)
    return conf

