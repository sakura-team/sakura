import bottle, urllib.request, urllib.error
import sakura.hub.conf as conf
from pathlib import Path

WEBCACHE_CDNS = {
    'cdnjs': 'https://cdnjs.cloudflare.com/ajax/libs'
}

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
            with urllib.request.urlopen(url) as web_f:
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
