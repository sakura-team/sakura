import random, time, gevent

class SecretManager:
    def __init__(self, registry, obj, lifetime):
        self.registry = registry
        self.obj = obj
        self.secret = random.getrandbits(32)
        self.lifetime = lifetime
    def live_and_die(self):
        gevent.sleep(self.lifetime)
        self.registry.remove(self.secret)

class SecretsRegistry:
    def __init__(self, default_lifetime):
        self.secrets = {}
        self.default_lifetime = default_lifetime
    def generate_secret(self, obj, lifetime = None):
        if lifetime == None:
            lifetime = self.default_lifetime
        sec = SecretManager(self, obj, lifetime)
        self.secrets[sec.secret] = sec
        gevent.Greenlet.spawn(sec.live_and_die)
        return sec.secret
    def get_obj(self, secret):
        sec = self.secrets.get(secret, None)
        if sec is not None:
            return sec.obj
    def remove(self, secret):
        del self.secrets[secret]
