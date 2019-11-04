import sys, smtplib, argparse
from email.message import EmailMessage
from subprocess import Popen, PIPE
from sakura.common.conf import merge_args_and_conf
from sakura.hub import set_conf, conf
from sakura.common.password import decode_password

def sendmail(receiver_email, subject, content):
    p = Popen(['sakura-hub-sendmail',
            '--conf-file', conf.conf_file_name,
            receiver_email, subject], stdin = PIPE)
    p.stdin.write(content.encode(sys.getdefaultencoding()))
    p.stdin.flush()
    p.stdin.close()

def load_hub_sendmail_conf():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conf-file',
                help="Specify alternate configuration file",
                type=argparse.FileType('r'),
                default='/etc/sakura/hub.conf')
    parser.add_argument("receiver_email", nargs=1)
    parser.add_argument("subject", nargs=1)
    set_conf(merge_args_and_conf(parser))

def run():
    load_hub_sendmail_conf()
    content = sys.stdin.read()
    login = conf.emailing.get('login', None)
    if login is not None:
        encoded_password = conf.emailing.get('encoded_password', None)
        if encoded_password is not None:
            password = decode_password(encoded_password)
        else:   # legacy clear-text password
            password = conf.emailing.password
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = '[sakura] ' + conf.subject[0]
    msg['From'] = conf.emailing.source
    msg['To'] = conf.receiver_email[0]
    if conf.emailing.ssl:
        cls = smtplib.SMTP_SSL
    else:
        cls = smtplib.SMTP
    s = cls(conf.emailing.host, conf.emailing.port)
    if login is not None:
        s.login(login, password)
    s.send_message(msg)
    s.quit()
