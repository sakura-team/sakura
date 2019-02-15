#!/usr/bin/env python3
import sys
from gevent import Greenlet
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
from sakura.daemon.engine import DaemonEngine
from sakura.daemon.greenlets import HubRPCGreenlet
from sakura.common.planner import PlannerGreenlet
from sakura.common.cache import Cache

def run():
    try:
        set_unbuffered_stdout()
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
