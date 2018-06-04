import itertools, csv, io, zlib

def stream_csv(header_labels, stream, gzip_compression=False):
    rows_transfered = 0
    bytes_transfered = 0
    # build pipeline
    s = b''
    out_buffer = io.BytesIO()
    txt_encoder = io.TextIOWrapper(out_buffer, write_through=True, encoding='utf-8')
    writer = csv.writer(txt_encoder)
    # we use zlib directly because we get better performance than with gzip module
    if gzip_compression:
        gz_filter = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, 31, memLevel=9)
    # header line
    writer.writerow(header_labels)
    # data rows...
    # note: we append a fake chunk 'None' at the end
    # because flushing gz_filter will generate
    # more output data.
    for chunk in itertools.chain(stream, (None,)):
        if chunk is not None:
            writer.writerows(chunk.tolist())
            rows_transfered += chunk.size
            if gzip_compression:
                s = gz_filter.compress(out_buffer.getbuffer())
            else:
                s = out_buffer.getvalue()
            out_buffer.truncate(0)
            out_buffer.seek(0)
        else:
            # flush pipeline
            if gzip_compression:
                s = gz_filter.flush()   # this will generate more output data
        if len(s) > 0:
            bytes_transfered += len(s)
            yield rows_transfered, bytes_transfered, s
            s = b''
    txt_encoder.close()
    out_buffer.close()
