import bottle, json, time
from gevent.socket import IPPROTO_TCP, TCP_NODELAY
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import rpc_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.web.cache import webcache_serve
from sakura.hub.web.csvtools import export_table_as_csv, export_stream_as_csv
from sakura.hub.web.video import serve_video_stream
from sakura.hub.db import db_session_wrapper
from sakura.common.tools import monitored
from pathlib import Path
from bottle import template
from collections import namedtuple
from sakura.hub import conf

def to_namedtuple(clsname, d):
    return namedtuple(clsname, d.keys())(**d)

class NoDelayWSHandler(WebSocketHandler):
    def __init__(self, sock, *args, **kwargs):
        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        super().__init__(sock, *args, **kwargs)

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    allowed_startup_urls = ('/', '/index.html')

    @monitored
    def ws_handle(proto_name):
        wsock = bottle_get_wsock()
        with db_session_wrapper():
            rpc_manager(context, wsock, proto_name)

    @app.route('/websocket')
    @app.route('/api-websocket')
    def ws_create():
        proto_name = bottle.request.query.protocol or 'json'
        ws_handle(proto_name)

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

    @app.route('/streams/<op_id:int>/opengl/<ogl_id:int>/video-<width:int>x<height:int>.mp4')
    def route_serve_video_stream(op_id, ogl_id, width, height):
        with db_session_wrapper():
            yield from serve_video_stream(context, op_id, ogl_id, width, height)

    @app.route('/modules/dataflows/templates/<filepath:path>', method=['POST'])
    def serve_template(filepath):
        params = json.loads(
                    bottle.request.forms['params'],
                    object_hook = lambda d: to_namedtuple('Params', d))
        with (Path(webapp_path) / 'modules' / 'dataflows' / 'templates' /filepath).open() as f:
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
        session_id_management_post(resp)
        return resp

    # session-id cookie management
    # ----------------------------
    def get_session_id_cookie():
        session_id = bottle.request.get_cookie("session-id")
        if session_id is None:
            return None
        try:
            return int(session_id)
        except ValueError:
            bottle.abort(401, 'Wrong session id.')

    # session-id management
    @app.hook('before_request')
    def session_id_management_pre():
        requested_session_id = get_session_id_cookie()
        #print(bottle.request.path, 'requested session id:', requested_session_id)
        with db_session_wrapper():
            if not context.attach_session(requested_session_id):
                # session-id cookie is not present or no longer valid
                if bottle.request.path in (allowed_startup_urls + ('/api-websocket',)):
                    # create a new session
                    context.new_session()
                    print(bottle.request.path, 'created a new session', context.session.id)
                if bottle.request.path == '/websocket':
                    bottle.abort(503, 'missing or invalid session cookie')

    @app.hook('after_request')
    def session_id_management_post(resp=bottle.response):
        requested_session_id = get_session_id_cookie()
        with db_session_wrapper():
            if context.session is not None:
                if requested_session_id != context.session.id and \
                        bottle.request.path in allowed_startup_urls:
                    print(bottle.request.path, 'let the browser update session id cookie', context.session.id)
                    resp.set_cookie("session-id", str(context.session.id))
        # Ensure the browser will always request the root document
        # (instead of using its cache), so that we can update the
        # session-id cookie in the response if needed.
        # The browser will then associate this possibly new session-id
        # to subsequent page requests.
        if bottle.request.path in allowed_startup_urls:
            resp.set_header("Cache-Control", "no-cache, must-revalidate")

    server = WSGIServer(('', conf.web_port), app,
                        handler_class=NoDelayWSHandler)
    server.start()
    ws_handle.catch_issues()
