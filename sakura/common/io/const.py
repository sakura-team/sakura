import builtins, numbers, numpy as np
from sakura.common.bottle import PicklableFileRequest

IO_TRANSFERABLES = (None.__class__, np.ndarray, numbers.Number, np.dtype, PicklableFileRequest) + \
                   tuple(getattr(builtins, t) for t in ( \
                        'bytearray', 'bytes', 'dict', 'frozenset', 'list',
                        'set', 'str', 'tuple', 'BaseException', 'type'))

IO_REQ_FUNC_CALL = 0
IO_REQ_ATTR = 1

IO_RESP_TRANSFERED = 2
IO_RESP_HELD = 3
IO_RESP_REQUEST_ERROR = 4
IO_RESP_STOP_ITERATION = 5

IO_ARG_TRANSFERED = 0
IO_ARG_HELD = 1
