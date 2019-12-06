import sys, json, pathlib, getpass, hashlib, base64, re
from sakura.common.errors import APIRequestError

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

def get_password(prompt):
    while True:
        password = getpass.getpass(prompt)
        if len(password.strip()) == 0:
            print("Sorry this field is required.")
            continue
        hashed = hashlib.sha256(password.encode(sys.stdin.encoding)).digest()
        return base64.b64encode(hashed).decode('ascii')

class ClientConf:
    def __init__(self):
        self.conf_path = pathlib.Path.home() / '.sakura' / 'client.conf'
        self.loaded_conf = None
    def __getattr__(self, attr):
        if self.loaded_conf is None:
            if not self.conf_path.exists():
                self.loaded_conf = {}
            else:
                print('Reading sakura client conf from ' + str(self.conf_path))
                self.loaded_conf = json.loads(self.conf_path.read_text())
        return self.loaded_conf.get(attr)
    def login(self, api):
        if self.username is not None:
            api.login(self.username, self.password_hash)
    def check(self, proxy, set_connect_timeout):
        if self.hub_url is None:
            set_connect_timeout(5)
            while True:
                self.loaded_conf['hub_url'] = input('Enter sakura platform URL: ').rstrip('/')
                try:
                    proxy.users.current.info()    # check an api request can reach hub
                except TimeoutError:
                    print('Please re-check.')
                    continue
                # ok, leave loop
                set_connect_timeout(None)
                break
            while True:
                answer = ''
                while answer not in ('yes', 'no'):
                    answer = input('Did you already register on this platform? [yes|no] ')
                try:
                    if answer == 'yes':
                        self.loaded_conf['username'] = input('Enter your sakura username: ')
                        self.loaded_conf['password_hash'] = get_password('Enter your sakura password: ')
                        # verify (this might raise APIRequestError if it fails)
                        self.login(proxy)
                    else:
                        print('Starting registration procedure...')
                        terms_url = self.hub_url + "/divs/documentation/cgu.html"
                        answer = ''
                        while answer not in ('yes', 'no'):
                            answer = input('Please confirm you accept the usage terms (%s) [yes|no]: ' % terms_url)
                        if answer == 'no':
                            print('Aborting.')
                            sys.exit()
                        while True:
                            self.loaded_conf['username'] = input('Enter a sakura username: ')
                            if self.loaded_conf['username'].strip() == '':
                                print("Sorry this field is required.")
                                continue
                            break
                        while True:
                            self.loaded_conf['password_hash'] = get_password('Enter a password: ')
                            repeated_password_hash = get_password('Repeat this password: ')
                            if self.loaded_conf['password_hash'] != repeated_password_hash:
                                print("Passwords do not match!")
                                continue
                            break
                        user_info = {
                            'login': self.loaded_conf['username'],
                            'password': self.loaded_conf['password_hash']
                        }
                        while True:
                            user_info['email'] = input('Enter your email: ')
                            if not EMAIL_REGEX.match(user_info['email']):
                                print("This does not seem a valid email.")
                                continue
                            break
                        for attr_field, attr_name, required in (
                                    ('first_name', 'first name', True),
                                    ('last_name', 'last name', True),
                                    ('country', 'country', False),
                                    ('institution', 'institution', False),
                                    ('occupation', 'occupation (job title)', False),
                                    ('work_domain', 'work domain', False)):
                            if required:
                                prompt = 'Enter your ' + attr_name + ': '
                            else:
                                prompt = 'Enter your ' + attr_name + ' (optional): '
                            while True:
                                user_info[attr_field] = input(prompt)
                                if required and user_info[attr_field].strip() == '':
                                    print("Sorry this field is required.")
                                    continue
                                break
                        # register user and login (this might raise APIRequestError if it fails)
                        proxy.users.create(**user_info)
                        self.login(proxy)
                except APIRequestError as e:
                    print(e)
                    continue
                # ok, leave loop
                break
            self.save()
    def save(self):
        self.conf_path.parent.mkdir(parents=True, exist_ok=True)
        self.conf_path.write_text(json.dumps(self.loaded_conf))
        self.conf_path.chmod(0o600)
        print('Config saved at ' + str(self.conf_path))

def get_conf():
    return ClientConf()
