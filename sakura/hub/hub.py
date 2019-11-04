#!/usr/bin/env python3
from sakura.common.bottle import fix_bottle
fix_bottle()

import os, sys, argparse
from gevent import Greenlet
from sakura.hub import set_conf, conf
from sakura.hub.context import HubContext
from sakura.hub.web.greenlet import web_greenlet
from sakura.hub.daemons.greenlet import daemons_greenlet
from sakura.hub.cleanup import plan_cleanup
from sakura.hub.db import instanciate_db, db_session_wrapper
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets, debug_ending_greenlets
from sakura.common.conf import merge_args_and_conf
from sakura.common.planner import PlannerGreenlet

DEBUG_ENDING_GREENLETS = False

def load_hub_conf():
    default_webapp_path = sys.prefix + '/sakura/web_interface'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conf-file',
                help="Specify alternate configuration file",
                type=argparse.FileType('r'),
                default='/etc/sakura/hub.conf')
    parser.add_argument('-d', '--webapp-dir',
                help="Specify web app directory",
                type=str,
                default=default_webapp_path)
    defaults = dict(
        work_dir = '/var/lib/sakura',
        mode = 'prod'
    )
    set_conf(merge_args_and_conf(parser, defaults))

def run():
    # load conf
    load_hub_conf()
    try:
        set_unbuffered_stdout()
        webapp_path = conf.webapp_dir
        # create hub db
        db = instanciate_db()
        # create planner greenlet
        planner_greenlet = PlannerGreenlet()
        # create shared context
        context = HubContext(db, planner_greenlet)
        with db_session_wrapper():
            context.restore()
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
    if DEBUG_ENDING_GREENLETS:
        debug_ending_greenlets()
