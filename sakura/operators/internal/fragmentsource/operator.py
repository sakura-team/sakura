#!/usr/bin/env python
from sakura.daemon.processing.operator import InternalOperator

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
        self.remote_out_table = remote_op.output_tables[remote_out_id]
    def construct(self):
        out_table_info = self.remote_out_table.get_info_serializable()
        # just one output, copy info from remote table
        self.output_table = self.register_output(
                out_table_info['label'], self.compute)
        self.output_table.length = out_table_info['length']
        for col_label, col_type in out_table_info['columns']:
            self.output_table.add_column(col_label, eval(col_type))
    def compute(self):
        # we just pull and transmit the output from the remote operator.
        # however, for performance reasons, we do not pull rows 1 by 1,
        # we pull FRAGMENT_BUFFER rows at a time.
        row_idx = 0
        last_row_idx = 0
        while True:
            for row in self.remote_out_table.get_range(row_idx, row_idx + FRAGMENT_BUFFER):
                yield row
                row_idx += 1
            if row_idx < last_row_idx + FRAGMENT_BUFFER:
                break
            last_row_idx += FRAGMENT_BUFFER
