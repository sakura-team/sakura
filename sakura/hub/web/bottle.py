import bottle
from sakura.common.io.serializer import Serializer

def bottle_get_wsock():
    wsock = bottle.request.environ.get('wsgi.websocket')
    if not wsock:
        bottle.abort(400, 'Expected WebSocket request.')
    return Serializer(wsock)
