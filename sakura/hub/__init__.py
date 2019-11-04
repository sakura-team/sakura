real_conf = None

def set_conf(in_conf):
    global real_conf
    real_conf = in_conf

class ConfProxy:
    def __getattr__(self, attr):
        return getattr(real_conf, attr)

conf = ConfProxy()
