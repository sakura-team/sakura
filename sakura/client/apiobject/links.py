from sakura.client.apiobject.base import APIObjectBase
from sakura.client.apiobject.observable import APIObservableEvent
from sakura.client.events import set_event_callback

class APILink:
    _known = {}
    _deleted = set()
    def __new__(cls, remote_api, link_info):
        link_id = link_info['link_id']
        if link_id not in APILink._known:
            remote_obj = remote_api.links[link_id]
            short_desc = "%s[%d]->%s[%d]" % (
                    link_info['src_cls_name'],
                    link_info['src_out_id'],
                    link_info['dst_cls_name'],
                    link_info['dst_in_id'])
            def get_remote_obj():
                if link_id in APILink._deleted:
                    raise ReferenceError('This link was deleted!')
                else:
                    return remote_obj
            class APILinkImpl(APIObjectBase):
                __doc__ = 'Sakura Link - ' + short_desc
                def __get_remote_info__(self):
                    return get_remote_obj().info()
                def delete(self):
                    """Delete this link"""
                    get_remote_obj().delete()
                    APILink._deleted.add(link_id)
                def _activate_events(self):
                    events_obj_id = 'links[' + str(link_id) + ']'
                    if not getattr(self, '_events_activated', False):
                        get_remote_obj().monitor(events_obj_id)
                        set_event_callback(remote_api, events_obj_id, self._events_cb)
                        self._events_activated = True
                def _events_cb(self, evt_name, *evt_args, **evt_kwargs):
                    observable = None
                    if evt_name == 'enabled':
                        observable = self.on_enabled
                    elif evt_name == 'disabled':
                        observable = self.on_disabled
                    # note: other events are ignored
                    if observable is not None:
                        observable.notify()
                @property
                def on_enabled(self):
                    if not hasattr(self, '_on_enabled'):
                        self._on_enabled = APIObservableEvent()
                        self._activate_events()
                    return self._on_enabled
                @property
                def on_disabled(self):
                    if not hasattr(self, '_on_disabled'):
                        self._on_disabled = APIObservableEvent()
                        self._activate_events()
                    return self._on_disabled
            APILink._known[link_id] = APILinkImpl()
        return APILink._known[link_id]
