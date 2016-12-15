#!/usr/bin/env python3

import os, sys, gevent
from gevent import Greenlet
from hub.context import HubContext
from hub.web.greenlet import web_greenlet
from hub.daemons.greenlet import daemons_greenlet

CURDIR = os.path.dirname(os.path.abspath(__file__))

def run(webapp_path):
    # create shared context
    context = HubContext()
    # run greenlets and wait until they end.
    gevent.joinall((
            Greenlet.spawn(daemons_greenlet, context),
            Greenlet.spawn(web_greenlet, context, webapp_path),
    ))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        webapp_dir = 'basic_webapp'
    else:
        webapp_dir = sys.argv[1]
    webapp_path = CURDIR + '/' + webapp_dir
    run(webapp_path)
