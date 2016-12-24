import bottle
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from sakura.hub.web.manager import web_manager
from sakura.hub.web.bottle import bottle_get_wsock
from sakura.hub.tools import monitored

def web_greenlet(context, webapp_path):
    app = bottle.Bottle()

    @app.route('/websockets/gui')
    @monitored
    def handle_gui_websocket():
        wsock = bottle_get_wsock(bottle.request)
        web_manager(context, wsock)

    # if no route was found above, look for static files in webapp subdir
    @app.route('/')
    @app.route('/<filepath:path>')
    def server_static(filepath = 'index.html'):
        print('serving ' + filepath, end="")
        resp = bottle.static_file(filepath, root = webapp_path)
        print(' ->', resp)
        return resp

    server = WSGIServer(("0.0.0.0", 8081), app,
                        handler_class=WebSocketHandler)
    server.start()
    handle_gui_websocket.catch_issues()
