import time
import sakura.hub.conf as conf

class SessionMixin:
    UNUSED_DELAY = 360
    NUM_WS_PER_SESSION = {}

#    cote javascript : il faut toujours avoir au moins une
#    websocket libre. avant d utiliser la derniere, on envoie
#    une requete pour obtenir un secret temporaire permettant
#    d en creer une autre.

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
        print('Cleaned up session.')
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
        session = cls(timeout = timeout, user = user)
        context.db.commit()
        return session
    @classmethod
    def cleanup(cls):
        for session in cls.select():
            if not session.in_use:
                session.cleanup_session()
