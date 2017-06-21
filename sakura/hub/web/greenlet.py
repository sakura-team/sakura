import bottle, json
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import rpc_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.tools import monitored
from pathlib import Path
from bottle import template
from collections import namedtuple
import sakura.hub.conf as conf

def to_namedtuple(clsname, d):
    return namedtuple(clsname, d.keys())(**d)

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    @app.route('/websockets/rpc')
    @monitored
    def handle_rpc_websocket():
        wsock = bottle_get_wsock(bottle.request)
        rpc_manager(context, wsock)

    @app.route('/opfiles/<op_id:int>/<filepath:path>')
    def serve_operator_file(op_id, filepath):
        print('serving operator %d file %s' % (op_id, filepath), end="")
        resp = context.serve_operator_file(op_id, filepath)
        print(' ->', resp.status_line)
        return resp

    @app.route('/tpl/<filepath:path>', method=['POST'])
    def serve_template(filepath):
        params = json.loads(
                    bottle.request.forms['params'],
                    object_hook = lambda d: to_namedtuple('Params', d))
        with (Path(webapp_path) / filepath).open() as f:
            return template(f.read(), **params._asdict())

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
    handle_rpc_websocket.catch_issues()
