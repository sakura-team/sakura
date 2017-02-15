import bottle
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import rpc_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.tools import monitored
import sakura.hub.conf as conf

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    @app.route('/websockets/rpc')
    @monitored
    def handle_rpc_websocket():
        wsock = bottle_get_wsock(bottle.request)
        rpc_manager(context, wsock)

    # if no route was found above, look for static files in webapp subdir
    @app.route('/')
    @app.route('/<filepath:path>')
    def server_static(filepath = 'index.html'):
        print('serving ' + filepath, end="")
        resp = bottle.static_file(filepath, root = webapp_path)
        print(' ->', resp.status_line)
        return resp

    server = WSGIServer(("0.0.0.0", conf.web_port), app,
                        handler_class=WebSocketHandler)
    server.start()
    handle_rpc_websocket.catch_issues()
