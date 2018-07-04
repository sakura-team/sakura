#!/usr/bin/env python3

import os, sys
from gevent import Greenlet
from sakura.hub.context import HubContext
from sakura.hub.web.greenlet import web_greenlet
from sakura.hub.daemons.greenlet import daemons_greenlet
from sakura.hub.cleanup import plan_cleanup
from sakura.hub.db import instanciate_db
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
from sakura.common.planner import PlannerGreenlet
import sakura.hub.conf as conf

def run():
    try:
        set_unbuffered_stdout()
        webapp_path = conf.webapp_dir
        # create hub db
        db = instanciate_db()
        # create planner greenlet
        planner_greenlet = PlannerGreenlet()
        # create shared context
        context = HubContext(db, planner_greenlet)
        # run greenlets and wait until they end.
        g1 = planner_greenlet.spawn()
        g2 = Greenlet.spawn(daemons_greenlet, context)
        g3 = Greenlet.spawn(web_greenlet, context, webapp_path)
        # register periodic tasks
        plan_cleanup()
        print('Started.')
        wait_greenlets(g1,g2,g3)
    except KeyboardInterrupt:
        pass    # python already writes 'KeyboardInterrupt' on stdout
    print('**out**')

if __name__ == "__main__":
    run()
