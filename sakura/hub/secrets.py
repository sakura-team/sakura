import random, time, gevent, hashlib

class TemporarySecretManager:
    def __init__(self, registry, obj, lifetime):
        self.registry = registry
        self.obj = obj
        self.secret = random.getrandbits(32)
        self.lifetime = lifetime
    def live_and_die(self):
        gevent.sleep(self.lifetime)
        self.registry.remove(self.secret)

class TemporarySecretsRegistry:
    def __init__(self, default_lifetime):
        self.secrets = {}
        self.default_lifetime = default_lifetime
    def generate_secret(self, obj, lifetime = None):
        if lifetime == None:
            lifetime = self.default_lifetime
        sec = TemporarySecretManager(self, obj, lifetime)
        self.secrets[sec.secret] = sec
        gevent.Greenlet.spawn(sec.live_and_die)
        return sec.secret
    def get_obj(self, secret):
        sec = self.secrets.get(secret, None)
        if sec is not None:
            return sec.obj
    def remove(self, secret):
        del self.secrets[secret]

class OneTimeHashSecretsRegistry:
    def __init__(self):
        self.secrets = {}
    def save_object(self, obj, sec_hash):
        self.secrets[sec_hash] = obj
    def pop_object(self, secret):
        sec_hash = hashlib.sha256(secret).digest()
        obj = self.secrets.get(sec_hash, None)
        if obj is not None:
            del self.secrets[sec_hash]
        return obj
