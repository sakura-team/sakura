import requests, ldap3, ssl
from sakura.hub import conf
from sakura.common.errors import APIRequestError
from sakura.common.password import decode_password

def login(context, ticket, service):
    url = conf.cas.url
    if not url:
        raise APIRequestError('Hub error: Cannot find file <b>hub-authentification.conf</b>!')
        return None
    cas_format = 'JSON'
    x = requests.get(conf.cas.url+'?ticket='+ticket+'&format='+cas_format+'&service='+service)
    succ = x.text.find('authenticationSuccess')
    if succ != -1:
        print('CAS AUTHENTICATION SUCCESS')
        login = x.text.split('<cas:user>')[1].split('</cas:user>')[0]
        print('\t Login:', login)
        print()
        found = None
        all_u = tuple(u.pack() for u in context.users.select())
        for u in all_u:
            if u['login'] == login:
                found = u
        if found != None:
            context.session.user = context.users.from_login_or_email(login)
            return context.session.user.login
        else:
            print('\tNew user, asking to LDAP for informations ...')
            #We ask to LDAP
            if not hasattr(conf, 'ldap'):
                raise APIRequestError('<b>LDAP description missing!</b><br> You cannot use CAS authentification!')
            try:
                url = conf.ldap.url
                port = conf.ldap.port
                dn = conf.ldap.dn
                bdn = conf.ldap.binddn
                encoded_password = conf.ldap.get('encoded_password', None)
                if encoded_password is not None:
                    pw = decode_password(encoded_password)
                else:   # legacy clear-text password
                    pw = conf.ldap.password
                tls = None
                if conf.ldap.get('tls_version', None) == 'v1':
                    tls = ldap3.Tls(version = ssl.PROTOCOL_TLSv1)
            except Exception as e:
                raise APIRequestError('LDAP description error!', e)
                return None
            server = ldap3.Server(url+':'+port, tls=tls, get_info=ldap3.ALL, connect_timeout=30.0)
            try:
                conn = ldap3.Connection(server, user=bdn, password=pw)
            except Exception as e:
                raise APIRequestError('LDAP Connection Failed!')
                return None
            try:
                conn.bind()
            except Exception as e:
                raise APIRequestError('LDAP Connection Timeout!<br><b>'+login+'</b> cannot login!')
                return None
            entry = conn.search(dn, '(&(objectclass=person)(uid='+login+'))', attributes=['*'])
            if not entry:
                raise APIRequestError('<b>'+login+'</b> not found in LDAP server!')
                return None
            u = conn.entries[0]
            print(u['mail'])
            print(u['given name'])
            print(u['sn'])
            user_info = {   'login': login,
                            'password': '__CAS__',
                            'email': u['mail'],
                            'first_name': u['given name'],
                            'last_name': u['sn'] }
            if context.users.new_user(**user_info):
                context.session.user = context.users.from_login_or_email(login)
                return context.session.user.login
            return None
    else:
        print('CAS AUTHENTICATION FAILURE', x.text)
        return 'cas authentication failure'
