import json

class ConfContainer(object):
    def __iter__(self):
        return iter(self.__dict__)
    def items(self):
        return self.__dict__.items()

def merge_conf(conf, added_conf):
    for name, value in added_conf.items():
        name = name.replace('-', '_')
        # give priority to existing value if any
        if name not in conf or getattr(conf, name) == None:
            # if value is a dict, recursively call merge_conf on it.
            if isinstance(value, dict):
                conf_value = ConfContainer()
                merge_conf(conf_value, value)
                setattr(conf, name, conf_value)
            else:
                setattr(conf, name, value)

def merge_args_and_conf(parser, defaults=None):
    args_conf = parser.parse_args()
    file_conf = json.load(args_conf.conf_file)
    # priority is: args_conf > file_conf > defaults
    conf = args_conf
    del conf.conf_file
    merge_conf(conf, file_conf)
    if defaults != None:
        merge_conf(conf, defaults)
    return conf

