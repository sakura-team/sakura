import time, random
from sakura.hub import conf

INTMAX_LIMIT = 2147483648

class SessionMixin:
    UNUSED_DELAY = 360
    NUM_WS_PER_SESSION = {}

    @property
    def num_ws(self):
        if self.id not in SessionMixin.NUM_WS_PER_SESSION:
            SessionMixin.NUM_WS_PER_SESSION[self.id] = 0
        return SessionMixin.NUM_WS_PER_SESSION[self.id]
    @num_ws.setter
    def num_ws(self, value):
        SessionMixin.NUM_WS_PER_SESSION[self.id] = value
    @property
    def in_use(self):
        return self.num_ws > 0
    @property
    def expired(self):
        return time.time() > self.timeout

    def cleanup_session(self):
        print('Cleaning up session ' + str(self.id))
        if self.id in SessionMixin.NUM_WS_PER_SESSION:
            del SessionMixin.NUM_WS_PER_SESSION[self.id]
        self.delete()
    def renew(self):
        self.timeout = time.time() + SessionMixin.UNUSED_DELAY
    def end(self):
        self.timeout = time.time() - 1

    @classmethod
    def new_session(cls, context):
        timeout = time.time() + SessionMixin.UNUSED_DELAY
        # auto login if debug mode
        user = None
        if conf.mode == 'debug' and hasattr(conf.debug, 'autologin'):
            user = context.users.get(login = conf.debug.autologin)
        session_id = random.randrange(INTMAX_LIMIT)
        session = cls(id = session_id, timeout = timeout, user = user)
        context.db.commit()
        return session
    @classmethod
    def cleanup(cls):
        for session in cls.select():
            if not session.in_use and session.expired:
                session.cleanup_session()
