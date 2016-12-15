import bottle

def bottle_get_wsock(request):
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        bottle.abort(400, 'Expected WebSocket request.')
    return wsock
