import bottle, urllib.request, urllib.error
from sakura.hub import conf
from pathlib import Path
import socket
import gevent.socket
saved_create_connection = socket.create_connection

WEBCACHE_CDNS = {
    'cdnjs': 'https://cdnjs.cloudflare.com/ajax/libs'
}
EXT_CONNECTION_TIMEOUT = 5

def fix_create_connection(*args, **kwargs):
    # restore for next time
    socket.create_connection = saved_create_connection
    # create gevent-compliant socket
    res = gevent.socket.create_connection(*args, **kwargs)
    # return
    return res

def gevent_urlopen(*args, **kwargs):
    # temporary patch stdlib socket.create_connection()
    # to get gevent-compliant behaviour
    socket.create_connection = fix_create_connection
    # call urlopen
    return urllib.request.urlopen(*args, **kwargs)

def webcache_serve(cdn, filepath):
    webcache_dir = conf.work_dir + '/webcache/'
    cachesubpath = cdn + '/' + filepath
    cachepath = Path(webcache_dir + cachesubpath)
    # if file is missing in cache, we will download it
    if not cachepath.exists():
        # create parent dir if missing
        if not cachepath.parent.exists():
            cachepath.parent.mkdir(parents = True)
        url = WEBCACHE_CDNS[cdn] + '/' + filepath
        print('webcache: fetching ' + url)
        try:
            with gevent_urlopen(url, None, EXT_CONNECTION_TIMEOUT) as web_f:
                with cachepath.open(mode='wb') as cache_f:
                    cache_f.write(web_f.read())
        except urllib.error.HTTPError as e:
            return bottle.abort(e.code, e.msg)
        except urllib.error.URLError as e:
            return bottle.abort(502, e.reason)
    # serve the file from the cache
    resp = bottle.static_file('/' + cachesubpath, root = webcache_dir)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
