import bottle, json, time
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import rpc_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.web.cache import webcache_serve
from sakura.hub.web.csvtools import export_table_as_csv, export_stream_as_csv
from sakura.hub.db import db_session_wrapper
from sakura.common.tools import monitored
from pathlib import Path
from bottle import template
from collections import namedtuple
import sakura.hub.conf as conf

def to_namedtuple(clsname, d):
    return namedtuple(clsname, d.keys())(**d)

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    @monitored
    def ws_handle(session):
        wsock = bottle_get_wsock()
        rpc_manager(context, wsock, session)

    @app.route('/websockets/sessions/new')
    def ws_new_session():
        print('/websockets/sessions/new')
        session = None
        with db_session_wrapper():
            session = context.new_session()
        ws_handle(session)

    @app.route('/websockets/sessions/connect')
    def ws_connect_session():
        if 'session-secret' not in bottle.request.query:
            raise bottle.HTTPError(400, 'session secret not specified.')
        secret = bottle.request.query.get('session-secret')
        print('/websockets/sessions/connect', secret)
        session = None
        with db_session_wrapper():
            session = context.recover_session(secret)
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

    @app.route('/streams/<op_id:int>/input/<in_id:int>/export.csv')
    def exp_in_stream_as_csv(op_id, in_id):
        with db_session_wrapper():
            yield from export_stream_as_csv(context, op_id, 0, in_id)

    @app.route('/streams/<op_id:int>/input/<in_id:int>/export.csv.gz')
    def exp_in_stream_as_csv_gz(op_id, in_id):
        with db_session_wrapper():
            yield from export_stream_as_csv(context, op_id, 0, in_id, True)

    @app.route('/streams/<op_id:int>/output/<out_id:int>/export.csv')
    def exp_out_stream_as_csv(op_id, out_id):
        with db_session_wrapper():
            yield from export_stream_as_csv(context, op_id, 1, out_id)

    @app.route('/streams/<op_id:int>/output/<out_id:int>/export.csv.gz')
    def exp_out_stream_as_csv_gz(op_id, out_id):
        with db_session_wrapper():
            yield from export_stream_as_csv(context, op_id, 1, out_id, True)

    @app.route('/tables/<table_id:int>/export.csv')
    def exp_table_as_csv(table_id):
        with db_session_wrapper():
            yield from export_table_as_csv(context, table_id)

    @app.route('/tables/<table_id:int>/export.csv.gz')
    def exp_table_as_csv_gz(table_id):
        with db_session_wrapper():
            yield from export_table_as_csv(context, table_id, gzip_compression=True)

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
