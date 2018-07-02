import smtplib
from email.message import EmailMessage
import sakura.hub.conf as conf
from sakura.common.password import decode_password

def sendmail(receiver_email, subject, content):
    login = conf.emailing.get('login', None)
    if login is not None:
        encoded_password = conf.emailing.get('encoded_password', None)
        if encoded_password is not None:
            password = decode_password(encoded_password)
        else:   # legacy clear-text password
            password = conf.emailing.password
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = '[sakura] ' + subject
    msg['From'] = conf.emailing.source
    msg['To'] = receiver_email
    if conf.emailing.ssl:
        cls = smtplib.SMTP_SSL
    else:
        cls = smtplib.SMTP
    s = cls(conf.emailing.host, conf.emailing.port)
    if login is not None:
        s.login(login, password)
    s.send_message(msg)
    s.quit()
