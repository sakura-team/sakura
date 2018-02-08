import smtplib
from email.message import EmailMessage
import sakura.hub.conf as conf

def sendmail(receiver_email, subject, content):
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
    s.login(conf.emailing.login, conf.emailing.password)
    s.send_message(msg)
    s.quit()
