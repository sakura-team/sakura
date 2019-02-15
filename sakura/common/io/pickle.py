import pickle, builtins, numbers, numpy as np
from sakura.common.errors import IOHoldException
from sakura.common.io.const import IO_TRANSFERED

IO_TRANSFERABLES = (None.__class__, np.ndarray, numbers.Number, np.dtype) + \
                   tuple(getattr(builtins, t) for t in ( \
                        'bytearray', 'bytes', 'dict', 'frozenset', 'list',
                        'set', 'str', 'tuple', 'BaseException', 'type'))

class PickleLocalAPIProtocol:
    @staticmethod
    def load(f):
        return pickle.load(f)
    @staticmethod
    def dump(res_info, f):
        if res_info[1] == IO_TRANSFERED and \
                not isinstance(res_info[2], IO_TRANSFERABLES):
            # res probably should not be serialized,
            # hold it locally.
            raise IOHoldException
        return pickle.dump(res_info, f)
