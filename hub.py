#!/usr/bin/env python3

import os, sys
from gevent import Greenlet
from sakura.hub.context import HubContext
from sakura.hub.web.greenlet import web_greenlet
from sakura.hub.daemons.greenlet import daemons_greenlet
from sakura.hub.cleanup import cleanup_greenlet
from sakura.hub.db import instanciate_db
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
import sakura.hub.conf as conf

CURDIR = os.path.dirname(os.path.abspath(__file__))

def run(webapp_path):
    # create hub db
    db = instanciate_db()
    # create shared context
    context = HubContext(db)
    # run greenlets and wait until they end.
    g1 = Greenlet.spawn(daemons_greenlet, context)
    g2 = Greenlet.spawn(web_greenlet, context, webapp_path)
    g3 = Greenlet.spawn(cleanup_greenlet, context)
    wait_greenlets(g1,g2,g3)
    print('**out**')

if __name__ == "__main__":
    try:
        set_unbuffered_stdout()
        print('Started.')
        webapp_path = CURDIR + '/' + conf.WEBAPP
        run(webapp_path)
    except KeyboardInterrupt:
        pass    # python already writes 'KeyboardInterrupt' on stdout
