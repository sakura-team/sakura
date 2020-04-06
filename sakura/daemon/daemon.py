#!/usr/bin/env python3
from sakura.common.bottle import fix_bottle
fix_bottle()

import sys
from gevent import Greenlet
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets, debug_ending_greenlets
from sakura.daemon.pdb import hook_pdb
from sakura.daemon.engine import DaemonEngine
from sakura.daemon.greenlets import HubRPCGreenlet
from sakura.common.planner import PlannerGreenlet
from sakura.common.cache import Cache
from sakura.daemon.db.pool import ConnectionPool
from sakura.common.streams import enable_standard_streams_redirection

DEBUG_ENDING_GREENLETS = False

def run():
    try:
        hook_pdb()
        set_unbuffered_stdout()
        enable_standard_streams_redirection()
        print('Starting...')

        # load data, create engine
        engine = DaemonEngine()

        # instanciate greenlets
        hub_greenlet = HubRPCGreenlet(engine)
        planner_greenlet = PlannerGreenlet()

        # prepare greenlets
        #try:
        if True:
            hub_greenlet.prepare()
            Cache.plan_cleanup(planner_greenlet)
            ConnectionPool.plan_cleanup(planner_greenlet)
        #except Exception as e:
        #    sys.stderr.write('ERROR: %s\nAborting.\n' % str(e))
        #    sys.exit()

        print('Started.')
        # spawn them and wait until they end.
        wait_greenlets( hub_greenlet.spawn(),
                        planner_greenlet.spawn())
    except KeyboardInterrupt:
        pass    # python already writes 'KeyboardInterrupt' on stdout
    print('**out**')

if __name__ == "__main__":
    run()
    if DEBUG_ENDING_GREENLETS:
        debug_ending_greenlets()
