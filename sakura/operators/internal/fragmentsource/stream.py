from sakura.daemon.processing.streams.output.base import OutputStreamBase
import numpy as np

DEFAULT_CHUNK_SIZE = 1000   # network is involved, do not increase too much

class FragmentSourceStream(OutputStreamBase):
    def __init__(self, remote_out_stream, src_col_indexes=None, filters=()):
        self.remote_out_stream = remote_out_stream
        out_stream_info = remote_out_stream.get_info_serializable()
        OutputStreamBase.__init__(self, out_stream_info['label'])
        self.length = out_stream_info['length']
        self.src_col_indexes = src_col_indexes
        self.filters = filters
        for src_col_index, col_info in enumerate(out_stream_info['columns']):
            if src_col_indexes is None or src_col_index in src_col_indexes:
                col_label, col_type, col_tags = col_info
                self.add_column(col_label, np.dtype(col_type), col_tags)
    def __iter__(self):
        for chunk in self.chunks():
            yield from chunk
    def chunks(self, chunk_size = DEFAULT_CHUNK_SIZE, offset=0):
        # we just pull and transmit the chunks from the remote operator.
        while True:
            chunk = self.remote_out_stream.get_range(
                    offset,
                    offset + chunk_size,
                    columns=self.src_col_indexes,
                    filters=self.filters)
            yield chunk
            if chunk.size < chunk_size:
                break
            offset += chunk_size
    def __select_columns__(self, *col_indexes):
        if self.src_col_indexes is None:
            src_col_indexes = col_indexes
        else:
            # subset of a subset of columns...
            src_col_indexes = \
                tuple(self.src_col_indexes[i] for i in col_indexes)
        return FragmentSourceStream(
            self.remote_out_stream,
            src_col_indexes,
            self.filters
        )
    def __filter__(self, col_index, comp_op, other):
        return FragmentSourceStream(
            self.remote_out_stream,
            self.src_col_indexes,
            self.filters + ((col_index, comp_op, other),)
        )
