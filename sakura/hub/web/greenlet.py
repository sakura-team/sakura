import bottle, json, time
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import rpc_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.web.cache import webcache_serve
from sakura.hub.db import db_session_wrapper
from sakura.hub.exceptions import TransferAborted
from sakura.hub.context import greenlet_env
from sakura.common.tools import monitored
from sakura.common.errors import APIRequestError, APIObjectDeniedError
from pathlib import Path
from bottle import template
from collections import namedtuple
import sakura.hub.conf as conf

def to_namedtuple(clsname, d):
    return namedtuple(clsname, d.keys())(**d)

def http_set_file_name(file_name):
    bottle.response.set_header('content-disposition',
                'attachment; filename="%s"' % file_name)

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    @monitored
    def ws_handle(session):
        wsock = bottle_get_wsock()
        rpc_manager(context, wsock, session)

    @app.route('/websockets/sessions/new')
    def ws_new_session():
        session = None
        with db_session_wrapper():
            session = context.new_session()
        ws_handle(session)

    @app.route('/websockets/sessions/connect/<secret:int>')
    def ws_connect_session(secret):
        session = None
        with db_session_wrapper():
            session = context.get_session(secret)
        if session is None:
            bottle.abort(401, 'Wrong secret.')
        ws_handle(session)

    @app.route('/opfiles/<op_id:int>/<filepath:path>')
    def serve_operator_file(op_id, filepath):
        print('serving operator %d file %s' % (op_id, filepath), end="")
        with db_session_wrapper():
            resp = context.serve_operator_file(op_id, filepath)
        print(' ->', resp.status_line)
        return resp

    @app.route('/tables/<table_id:int>/export.csv')
    def export_table_as_csv(table_id):
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
            with db_session_wrapper():
                table = context.tables.get(id=table_id)
                if table is None:
                    raise bottle.HTTPError(404, 'Invalid table identifier.')
                yield from table.stream_csv(
                        transfer, file_name_record_cb=http_set_file_name)
            print(' -> table transfer done (%ds)' % int(time.time()-startup))
        except TransferAborted:
            print(' -> table transfer user-aborted!')
        except APIObjectDeniedError as e:
            raise bottle.HTTPError(403, str(e))
        except APIRequestError as e:
            raise bottle.HTTPError(400, str(e))

    @app.route('/modules/workflow/tpl/<filepath:path>', method=['POST'])
    def serve_template(filepath):
        params = json.loads(
                    bottle.request.forms['params'],
                    object_hook = lambda d: to_namedtuple('Params', d))
        with (Path(webapp_path) / 'modules' / 'workflow' / filepath).open() as f:
            return template(f.read(), **params._asdict())

    @app.route('/webcache/cdnjs/<filepath:path>')
    def serve_cdnjs_cache(filepath):
        return webcache_serve('cdnjs', filepath)

    # if no route was found above, look for static files in webapp subdir
    @app.route('/')
    @app.route('/<filepath:path>')
    def serve_static(filepath = 'index.html'):
        print('serving ' + filepath, end="")
        resp = bottle.static_file(filepath, root = webapp_path)
        print(' ->', resp.status_line)
        return resp

    server = WSGIServer(("0.0.0.0", conf.web_port), app,
                        handler_class=WebSocketHandler)
    server.start()
    ws_handle.catch_issues()
