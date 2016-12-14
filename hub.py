#!/usr/bin/env python3

import os, sys, bottle, gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from hub.daemons.manager import daemon_manager
from hub.gui.manager import gui_manager
from hub.bottle import bottle_get_wsock
from hub.context import HubContext

CURDIR = os.path.dirname(os.path.abspath(__file__))

def run(webapp_path):
    app = bottle.Bottle()

    context = HubContext()

    @app.route('/websockets/daemon')
    def handle_daemon_websocket():
        global next_daemon_id
        wsock = bottle_get_wsock(bottle.request)
        daemon_id = context.get_daemon_id()
        daemon_manager(daemon_id, context, wsock)

    @app.route('/websockets/gui')
    def handle_gui_websocket():
        wsock = bottle_get_wsock(bottle.request)
        gui_manager(context, wsock)

    # if no route was found above, look for static files in webapp subdir
    @app.route('/')
    @app.route('/<filepath:path>')
    def server_static(filepath = 'index.html'):
        print('serving ' + filepath)
        return bottle.static_file(filepath, root = webapp_path)

    server = WSGIServer(("0.0.0.0", 8081), app,
                        handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        webapp_dir = 'basic_webapp'
    else:
        webapp_dir = sys.argv[1]
    webapp_path = CURDIR + '/' + webapp_dir
    run(webapp_path)
