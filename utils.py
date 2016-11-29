
log_id = 0

def ecrire(t):
    global log_id
    print log_id, " -\t", t
    log_id += 1


class AutoEnum(dict):
    __all_enums = []
    def __init__(self):
        self.__enum_id = len(AutoEnum.__all_enums)
        AutoEnum.__all_enums.append(self)
        self.__i__ = -1
    def __getattr__(self, name):
        if self.has_key(name):
            return dict.__getitem__(self, name)
        else:
            self.__i__ += 1
            dict.__setitem__(self, name, self.__i__)
            return self.__i__
    def __getitem__(self, name):
        return self.__getattr__(name)
    @staticmethod
    def get(enum_id):
        return AutoEnum.__all_enums__[enum_id]


class ServerSakuraIterator(object):
    def __init__(self, srv_op):
        self.srv_op = srv_op
        self.i = 0
    def next(self):
        res = self.srv_op.get_result(self.i)
        if res == None:
            raise StopIteration
        self.i += 1
        return tuple(res)


class ServerSakuraStepByStepOperator(object):
    def __init__(self):
        self.source_ops = None
    def set_source_op(self, in_id, source_op):
        if not self.source_ops:
            self.source_ops = [None] * (in_id+1)
        elif len(self.source_ops) < in_id+1:
            self.source_ops += [None] * (in_id+1 - len(self.source_ops))
        self.source_ops[in_id] = source_op
    def set_source_ops(self, source_ops):
        self.source_ops = source_ops
    def __iter__(self):
        return self.get_iterator()
    def get_iterator(self):
        return ServerSakuraIterator(self)


class ServerSakuraOneStepOperator(ServerSakuraStepByStepOperator):
    def __init__(self):
        ServerSakuraStepByStepOperator.__init__(self)
        self.result = None
    def get_result(self, i):
        if self.result == None:
            self.result = self.compute()
        if i < len(self.result):
            return self.result[i]
        else:
            return None
