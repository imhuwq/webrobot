import smtplib
from email.mime.text import MIMEText

from threading import Thread


class Email:
    def __init__(self, app):
        self.app = app

        email_settings = self.app.settings.get('email')

        self.sender = email_settings.get('user')
        self.user = email_settings.get('user')
        self.password = email_settings.get('password')
        self.host = email_settings.get('host')
        self.port = email_settings.get('port')

        self.receiver = None
        self.subject = None
        self.content = None

        self.msg = None

    def write(self, receiver, subject, content):
        self.receiver = receiver
        self.subject = subject
        self.content = content

        self.msg = MIMEText(content)
        self.msg['Subject'] = self.subject
        self.msg['From'] = self.sender
        self.msg['To'] = self.receiver

    def _send(self):
        if isinstance(self.msg, MIMEText):
            server = smtplib.SMTP_SSL(self.host, self.port)
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receiver, msg=self.msg.as_string())
            server.quit()
        else:
            raise Exception('Please write your message before you send it')

    def send(self):
        thread = Thread(target=self._send)
        thread.start()
