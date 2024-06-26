import smtplib
from email.message import EmailMessage

from django.conf import settings


def send_email(subject, message, recipient):
    smtp = settings.EMAIL_HOST
    login = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_ADMIN
    msg['To'] = recipient

    s = smtplib.SMTP_SSL(smtp)
    s.login(login, password)
    s.send_message(msg)
    s.quit()

