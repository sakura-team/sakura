import gevent
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
        return ActorCaller(self.actor, self.inbox, path)
    def __call__(self, *args, **kwargs):
        queue = Queue()
        self.inbox.put((queue, self.path, args, kwargs))
        return queue.get()

class Actor(ActorCaller):
    def __init__(self, obj):
        inbox = Queue()
        ActorCaller.__init__(self, None, inbox, ())
        def run(inbox, root_obj):
            while True:
                if DEBUG:
                    print(gevent.getcurrent().name, 'waiting')
                queue, path, args, kwargs = inbox.get()
                if DEBUG:
                    print(gevent.getcurrent().name, 'got', path, args, kwargs)
                if queue is None:
                    break
                obj = root_obj
                for attr in path:
                    obj = getattr(obj, attr)
                res = obj(*args, **kwargs)
                queue.put(res)
            if DEBUG:
                print(gevent.getcurrent().name, 'actor end')
        gevent.spawn(run, inbox, obj)
    def __del__(self):
        if DEBUG:
            print('actor del')
        self.inbox.put((None, None, None, None))

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
