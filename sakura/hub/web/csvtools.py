import bottle, re, time
from sakura.hub.context import greenlet_env
from sakura.hub.exceptions import TransferAborted
from sakura.common.errors import APIRequestError, APIObjectDeniedError

def http_set_file_name(obj_name, gzip_compression):
    extension = '.csv.gz' if gzip_compression else '.csv'
    file_name = re.sub(r'[^a-z0-9]', '-', obj_name.lower()) + extension
    bottle.response.set_header('content-disposition',
                'attachment; filename="%s"' % file_name)
    content_type = 'application/octet-stream' if gzip_compression \
                            else 'text/csv; charset=utf-8'
    bottle.response.content_type = content_type

def get_transfer(context):
    if 'transfer' not in bottle.request.query:
        raise bottle.HTTPError(400, 'transfer identifier not specified.')
    transfer_id = int(bottle.request.query.transfer)
    transfer = context.transfers.get(transfer_id, None)
    if transfer is None:
        raise bottle.HTTPError(400, 'Invalid transfer identifier.')
    return transfer

def csv_export_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            startup = time.time()
            yield from func(*args, **kwargs)
            print(' -> transfer done (%ds)' % int(time.time()-startup))
        except TransferAborted:
            print(' -> transfer user-aborted!')
        except APIObjectDeniedError as e:
            raise bottle.HTTPError(403, str(e))
        except APIRequestError as e:
            raise bottle.HTTPError(400, str(e))
    return wrapper

@csv_export_wrapper
def export_table_as_csv(context, table_id, gzip_compression=False):
    transfer = get_transfer(context)
    greenlet_env.session_id = transfer.session_id
    print('exporting table %d as csv...' % table_id)
    table = context.tables.get(id=table_id)
    if table is None:
        raise bottle.HTTPError(404, 'Invalid table identifier.')
    http_set_file_name(table.name, gzip_compression)
    yield from table.stream_csv(transfer, gzip_compression)

@csv_export_wrapper
def export_stream_as_csv(context, op_id, stream_type, stream_idx, gzip_compression=False):
    transfer = get_transfer(context)
    greenlet_env.session_id = transfer.session_id
    print('exporting stream as csv...')
    op = context.op_instances.get(id=op_id)
    if op is None:
        raise bottle.HTTPError(404, 'Invalid operator identifier.')
    op_info = op.pack()
    if stream_type == 0:
        streams_info = op_info['inputs']
    else:
        streams_info = op_info['outputs']
    if stream_idx < 0 or stream_idx >= len(streams_info):
        raise bottle.HTTPError(404, 'No such operator stream.')
    if stream_type == 0:
        stream = op.input_streams[stream_idx]
    else:
        stream = op.output_streams[stream_idx]
    http_set_file_name(stream.get_label(), gzip_compression)
    rows_estimate = stream.get_length()
    if rows_estimate is None:
        rows_estimate = -1
    csv_stream = stream.stream_csv(gzip_compression)
    for rows_transfered, bytes_transfered, s in csv_stream:
        transfer.notify_status(rows_transfered, rows_estimate, bytes_transfered)
        yield s
    transfer.notify_done()
