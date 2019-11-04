import json

class ConfContainer(object):
    def __iter__(self):
        return iter(self.__dict__)
    def items(self):
        return self.__dict__.items()
    def get(self, name, default=None):
        return self.__dict__.get(name, default)
    def keys(self):
        return self.__dict__.keys()
    def __getitem__(self, key):
        return self.__dict__[key]

def nomalize_conf_value(val):
    if hasattr(val, 'items'):
        # dict-like
        norm_val = ConfContainer()
        for name, value in val.items():
            name = name.replace('-', '_')
            setattr(norm_val, name, nomalize_conf_value(value))
        return norm_val
    elif isinstance(val, list):
        return list(nomalize_conf_value(item) for item in val)
    return val

def merge_conf(conf, added_conf):
    added_conf = nomalize_conf_value(added_conf)
    for name, value in added_conf.items():
        # give priority to existing value if any
        if name not in conf or getattr(conf, name) == None:
            setattr(conf, name, value)

def merge_args_and_conf(parser, defaults=None):
    args_conf = parser.parse_args(namespace=ConfContainer())
    file_conf = json.load(args_conf.conf_file)
    args_conf.conf_file.close()
    # priority is: args_conf > file_conf > defaults
    conf = ConfContainer()
    merge_conf(conf, args_conf)
    conf.conf_file_name = conf.conf_file.name
    del conf.conf_file
    merge_conf(conf, file_conf)
    if defaults != None:
        merge_conf(conf, defaults)
    return conf

