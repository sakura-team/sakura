import json

def merge_args_and_conf(parser, defaults=None):
    args_conf = parser.parse_args()
    file_conf = json.load(args_conf.conf_file)

    conf = args_conf
    del conf.conf_file
    for name, value in file_conf.items():
        name = name.replace('-', '_')
        # prefer the value specified in the command line if any
        if name not in conf or getattr(conf, name) == None:
            setattr(conf, name, value)

    if defaults != None:
        for name, value in defaults.items():
            if name not in conf:
                setattr(conf, name, value)

    return conf

