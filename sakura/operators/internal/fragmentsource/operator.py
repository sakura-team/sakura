#!/usr/bin/env python
from sakura.daemon.processing.operator import InternalOperator
from .stream import FragmentSourceStream

# This internal operator (not accessible from users)
# is used when a user links 2 operators running in
# 2 differents daemons. As a result, each daemon
# is running a fragment of the workflow, and the
# hub, together with this operator, passes the data
# between these fragments.
# The FragmentSourceOperator is internally added as
# a source of the 2nd workflow fragment.
# It pulls data from the hub (and the hub pulls data
# from the output of the 1st fragment) and passes this
# data to the next operator of the 2nd fragment.

FRAGMENT_BUFFER = 1000

class FragmentSourceOperator(InternalOperator):
    def __init__(self, hub, remote_op_id, remote_out_id):
        super().__init__()
        remote_op = hub.context.op_instances[remote_op_id]
        self.remote_out_stream = remote_op.output_streams[remote_out_id]
    def construct(self):
        # just one output, copy info from remote stream
        self.output_stream = self.register_output(
                FragmentSourceStream(self.remote_out_stream))
