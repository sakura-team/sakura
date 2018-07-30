#!/usr/bin/env python3
import sys
from gevent import Greenlet
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
from sakura.daemon.engine import DaemonEngine
from sakura.daemon.greenlets import \
            RPCServerGreenlet, RPCClientGreenlet
from sakura.common.planner import PlannerGreenlet
from sakura.common.cache import Cache

def run():
    try:
        set_unbuffered_stdout()
        print('Starting...')

        # load data, create engine
        engine = DaemonEngine()

        # instanciate greenlets
        server_greenlet = RPCServerGreenlet(engine)
        client_greenlet = RPCClientGreenlet(engine)
        planner_greenlet = PlannerGreenlet()

        # prepare greenlets
        #try:
        if True:
            server_greenlet.prepare()
            client_greenlet.prepare()
            Cache.plan_cleanup(planner_greenlet)
        #except Exception as e:
        #    sys.stderr.write('ERROR: %s\nAborting.\n' % str(e))
        #    sys.exit()

        print('Started.')
        # spawn them and wait until they end.
        wait_greenlets( server_greenlet.spawn(),
                        client_greenlet.spawn(),
                        planner_greenlet.spawn())
    except KeyboardInterrupt:
        pass    # python already writes 'KeyboardInterrupt' on stdout
    print('**out**')

if __name__ == "__main__":
    run()
