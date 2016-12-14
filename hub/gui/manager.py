import json, collections
from common.wsapi import LocalAPIHandler
from hub.gui.api import GuiToHubAPI

# the GUI passes a callback ID when issuing a request,
# and expects this ID to be returned with the result.
# we have to specialize the LocalAPIHandler for this.

ParsedGuiRequest = collections.namedtuple('ParsedGuiRequest',
                    ('cb_id', 'path', 'args', 'kwargs'))

class LocalGuiAPIHandler(LocalAPIHandler):
    def parse_request(self, req):
        parsed_request = ParsedGuiRequest(*self.protocol.loads(req))
        print(parsed_request)
        return parsed_request
    def format_result(self, parsed_request, res):
        full_res = (parsed_request.cb_id, res)
        print(full_res)
        return self.protocol.dumps(full_res)

def gui_manager(context, wsock):
    print('GUI connected.')
    local_api = GuiToHubAPI(context)
    handler = LocalGuiAPIHandler(wsock, json, local_api)
    handler.loop()
    print('GUI disconnected.')

