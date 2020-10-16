import gevent, inspect
from gevent.queue import Queue

DEBUG = False

class ActorCaller:
    def __init__(self, actor, inbox, path):
        # we maintain a reference to the actor in order to ensure
        # it will not be garbage-collected before all ActorCallers
        # (since it manages lifetime of background greenlet)
        self._actor = actor
        self.inbox = inbox
        self.path = path
    @property
    def actor(self):
        if self._actor is None:
            return self
        return self._actor
    def __getattr__(self, attr):
        path = self.path + (attr,)
        queue = Queue()
        self.inbox.put((queue, 'ATTR', path))
        resp = queue.get()
        if resp[0] == 'EXCEPTION':
            raise resp[1]
        if resp[0] == 'ATTR':
            return resp[1]
        if resp[0] == 'METHOD':
            return ActorCaller(self.actor, self.inbox, path)
    def __call__(self, *args, **kwargs):
        queue = Queue()
        self.inbox.put((queue, 'CALL', self.path, args, kwargs))
        resp = queue.get()
        if resp[0] == 'EXCEPTION':
            raise resp[1]
        if resp[0] == 'RESULT':
            return resp[1]
    def __enter__(self):
        return self.__getattr__('__enter__')()
    def __exit__(self, exc_type, exc_value, traceback):
        return self.__getattr__('__exit__')(exc_type, exc_value, traceback)

class Actor(ActorCaller):
    def __init__(self, obj):
        inbox = Queue()
        ActorCaller.__init__(self, None, inbox, ())
        def process_one_request(inbox, root_obj):
            full_req = inbox.get()
            queue, req, path = full_req[:3]
            if DEBUG:
                print(gevent.getcurrent().name, 'got', full_req[1:])
            if queue is None:
                return False
            obj = root_obj
            try:
                for attr in path:
                    obj = getattr(obj, attr)
                if req == 'ATTR':
                    if inspect.ismethod(obj):
                        queue.put(('METHOD',))
                    else:
                        queue.put(('ATTR', obj))
                elif req == 'CALL':
                    args, kwargs = full_req[3:]
                    res = obj(*args, **kwargs)
                    queue.put(('RESULT', res))
            except Exception as e:
                queue.put(('EXCEPTION', e))
            return True
        def run(inbox, root_obj):
            while True:
                if DEBUG:
                    print(gevent.getcurrent().name, 'waiting')
                if not process_one_request(inbox, root_obj):
                    break
            if DEBUG:
                print(gevent.getcurrent().name, 'actor end')
        gevent.spawn(run, inbox, obj)
    def __del__(self):
        if DEBUG:
            print('actor del')
        self.inbox.put((None, None, None))

# The following decorator allows to turn a class into an 'actor'.
# All functions calls to such an object or its attributes will be
# handled in sequence by a background greenlet.
# It allows to solve concurrency problems when several greenlets
# are interacting with the same object.
def actor(cls):
    class cls_wrapper:
        def __call__(self, *args, **kwargs):
            obj = cls(*args, **kwargs)
            return Actor(obj)
        def __getattr__(self, attr):
            return getattr(cls, attr)
    return cls_wrapper()
