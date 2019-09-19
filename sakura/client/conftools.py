import sys, json, pathlib, getpass, hashlib, base64

CONF_FIELDS = (
    ('hub_host', lambda: input('Enter sakura-hub ip or hostname: ')),
    ('hub_port', lambda: int(input('Enter sakura-hub websocket port: '))),
    ('username', lambda: input('Enter your sakura username: ')),
    ('password_hash', lambda: get_password())
)

def get_password():
    password = getpass.getpass('Enter your sakura password: ')
    hashed = hashlib.sha256(password.encode(sys.stdin.encoding)).digest()
    return base64.b64encode(hashed).decode('ascii')

class ClientConf:
    def __init__(self):
        self.conf_path = pathlib.Path.home() / '.sakura' / 'client.conf'
        self.loaded_conf = None
    def __getattr__(self, attr):
        if self.loaded_conf is None:
            if not self.conf_path.exists():
                self.loaded_conf = {
                        item_name: item_request() \
                        for item_name, item_request in CONF_FIELDS
                }
                self.conf_path.parent.mkdir(parents=True, exist_ok=True)
                self.conf_path.write_text(json.dumps(self.loaded_conf))
                self.conf_path.chmod(0o600)
                print('Config saved at ' + str(self.conf_path))
            else:
                print('Reading sakura client conf from ' + str(self.conf_path))
                self.loaded_conf = json.loads(self.conf_path.read_text())
        return self.loaded_conf[attr]

def get_conf():
    return ClientConf()
