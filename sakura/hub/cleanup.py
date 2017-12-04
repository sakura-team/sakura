import gevent
from sakura.hub.db import db_session_wrapper

def cleanup_greenlet(context):
    while True:
        gevent.sleep(6)
        # cleanup obsolete sessions
        with db_session_wrapper():
            context.sessions.cleanup()
