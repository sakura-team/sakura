import bottle, re, time
from sakura.hub.context import greenlet_env
from sakura.hub.exceptions import TransferAborted
from sakura.common.errors import APIRequestError, APIObjectDeniedError

def http_set_file_name(file_name):
    bottle.response.set_header('content-disposition',
                'attachment; filename="%s"' % file_name)

def export_table_as_csv(context, table_id, gzip_compression=False):
    if 'transfer' not in bottle.request.query:
        raise bottle.HTTPError(400, 'transfer identifier not specified.')
    transfer_id = int(bottle.request.query.transfer)
    try:
        startup = time.time()
        transfer = context.transfers.get(transfer_id, None)
        if transfer is None:
            raise bottle.HTTPError(400, 'Invalid transfer identifier.')
        greenlet_env.session_id = transfer.session_id
        print('exporting table %d as csv...' % table_id)
        table = context.tables.get(id=table_id)
        if table is None:
            raise bottle.HTTPError(404, 'Invalid table identifier.')
        extension = '.csv.gz' if gzip_compression else '.csv'
        file_name = re.sub(r'[^a-z0-9]', '-', table.name.lower()) + extension
        http_set_file_name(file_name)
        yield from table.stream_csv(transfer, gzip_compression)
        print(' -> table transfer done (%ds)' % int(time.time()-startup))
    except TransferAborted:
        print(' -> table transfer user-aborted!')
    except APIObjectDeniedError as e:
        raise bottle.HTTPError(403, str(e))
    except APIRequestError as e:
        raise bottle.HTTPError(400, str(e))
