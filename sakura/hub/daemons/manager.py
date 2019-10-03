from sakura.common.tools import FAST_PICKLE as pickle
from sakura.hub.db import db_session_wrapper
from sakura.hub.daemons.api import DaemonToHubAPI
from sakura.hub.exceptions import DaemonDataError
from sakura.common.errors import APIRemoteError
from sakura.common.io import APIEndpoint

def on_daemon_connect(context, daemon_id):
    with db_session_wrapper():
        daemon = context.daemons[daemon_id]
        try:
            daemon.on_connect()
        except DaemonDataError as e:
            daemon.api.fire_data_issue(str(e))
        except APIRemoteError as e:
            print('on_daemon_connect() remote exception: ' + str(e))

def rpc_manager(context, daemon_name, sock_file):
    print('new rpc connection %s -> hub.' % daemon_name)
    local_api = DaemonToHubAPI(context)
    endpoint = APIEndpoint(sock_file, pickle, local_api,
                                session_wrapper = db_session_wrapper)
    with db_session_wrapper():
        daemon = context.get_daemon_from_name(daemon_name)
        context.attach_api_exception_handlers(endpoint)
        daemon.save_api(endpoint.proxy)
        # We will have to run daemon.on_connect()
        # but this greenlet cannot handle it because it may involve
        # IO messages on this endpoint we have to manage.
        # So we delegate this to the planner greenlet, and this greenlet
        # can focus on managing this endpoint.
        daemon_id = daemon.id
        context.planner.run_once(
               lambda: on_daemon_connect(context, daemon_id))
    # start endpoint management loop
    endpoint.loop()
    # loop has ended => daemon is disconnected!
    with db_session_wrapper():
        context.daemons[daemon_id].on_disconnect()
    print('rpc connection %s -> hub disconnected.' % daemon_name)
