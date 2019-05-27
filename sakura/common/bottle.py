import os.path, mimetypes, time, os
import sys, threading, gevent.local

# bottle uses thread-local-storage for HTTP request and
# response objects.
# in our context, we have greenlets, so bottle should
# use greenlet-local-storage instead.
# actually, we just have to fix the bottle import,
# since these request and response objects are created
# at this time.
def fix_bottle():
    if 'bottle' in sys.modules:
        sys.exit('Error: fix_bottle() called too late (bottle already imported)')
    saved_th_local = threading.local
    threading.local = gevent.local.local
    import bottle
    threading.local = saved_th_local

# When the hub receives a HTTP request for an operator's file,
# it has to transmit this request to the appropriate daemon,
# and the daemon handles this request.
# bottle request & response objects are not picklable, thus we
# use this object:
# * the hub creates the object (calls the __init__() function
#   using the bottle.request object and the requested filepath)
# * the object is transmitted to the daemon
# * the daemon calls the serve() function
# * the result is transmitted back to the hub
# * the hub transmits this result to the GUI in the form of a
#   bottle.HTTPResponse object.
class PicklableFileRequest:
    PASSED_ENVIRON = ('HTTP_IF_MODIFIED_SINCE',)
    def __init__(self, request, filepath):
        self.method = request.method
        self.environ = { k:v for k, v in request.environ.items() \
                            if k in PicklableFileRequest.PASSED_ENVIRON }
        self.filepath = filepath
    # this is inspired by bottle.static_file() function
    def serve(self, root_path, download=False, charset='UTF-8'):
        filename = os.path.join(root_path, self.filepath)
        headers = dict()
        if not os.path.exists(filename) or not os.path.isfile(filename):
            return False, 404, "File does not exist."
        if not os.access(filename, os.R_OK):
            return False, 403, "You do not have permission to access this file."

        mimetype, encoding = mimetypes.guess_type(filename)
        if encoding: headers['Content-Encoding'] = encoding

        if mimetype:
            if mimetype[:5] == 'text/' and charset and 'charset' not in mimetype:
                mimetype += '; charset=%s' % charset
            headers['Content-Type'] = mimetype

        if download:
            download = os.path.basename(filename if download == True else download)
            headers['Content-Disposition'] = 'attachment; filename="%s"' % download

        stats = os.stat(filename)
        headers['Content-Length'] = stats.st_size
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
        headers['Last-Modified'] = lm

        ims = self.environ.get('HTTP_IF_MODIFIED_SINCE')
        if ims:
            from bottle import parse_date
            ims = parse_date(ims.split(";")[0].strip())
        if ims is not None and ims >= int(stats.st_mtime):
            headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
            return True, '', 304, headers

        if self.method == 'HEAD':
            body = ''
        else:
            with open(filename, 'rb') as f:
                body = f.read()

        return True, body, None, headers
