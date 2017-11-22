#!/usr/bin/env python3
import sys
from gevent import Greenlet
from sakura.common.tools import set_unbuffered_stdout, \
                                wait_greenlets
from sakura.daemon.loading import load_operator_classes, \
                                load_datastores
from sakura.daemon.engine import DaemonEngine
from sakura.daemon.greenlets import \
            RPCServerGreenlet, RPCClientGreenlet

def run():
    set_unbuffered_stdout()
    print('Starting...')

    # load data, create engine
    op_classes = load_operator_classes()
    datastores = load_datastores()
    engine = DaemonEngine(op_classes, datastores)

    # prepare greenlets
    g1 = RPCServerGreenlet(engine)
    g2 = RPCClientGreenlet(engine)
    try:
        g1.prepare()
        g2.prepare()
    except Exception as e:
        sys.stderr.write('ERROR: %s\nAborting.\n' % str(e))
        sys.exit()

    print('Started.')
    # spawn them and wait until they end.
    wait_greenlets(g1.spawn(),g2.spawn())
    print('**out**')

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass    # python already writes 'KeyboardInterrupt' on stdout
