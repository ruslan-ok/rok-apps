"""Background process

A regular call to the API method that provides the operation of various site services.
"""
import os, requests, time, smtplib, json
from datetime import datetime
from email.message import EmailMessage

def console_log(status, mess=None):
    print(datetime.now().strftime('%Y.%m.%d %H:%M') + ' ' + status)
    if mess:
        print(mess)

def notify(host, user, pwrd, recipients, status, mess, maintype='text', subtype='plain'):
    host = os.environ.get('DJANGO_HOST')
    if host == 'localhost' and subtype != 'html':
        return console_log(status, mess)
    host_mail = os.environ.get('DJANGO_HOST_MAIL')
    s = smtplib.SMTP(host=host_mail, port=25)
    s.starttls()
    s.login(user, pwrd)
    msg = EmailMessage()
    msg['From'] = user
    msg['To'] = recipients
    msg['Subject']='Services Notificator: ' + status
    if subtype == 'plain':
        msg.set_content('Background process (/service/_service.py):\n\n' + mess)
    else:
        msg.set_content(mess, maintype=maintype, subtype=subtype)
    s.send_message(msg)
    del msg
    s.quit()

if (__name__ == '__main__'):
    api_host = os.environ.get('DJANGO_HOST_API')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN')
    verify = os.environ.get('DJANGO_CERT')
    mail_host = os.environ.get('DJANGO_HOST_MAIL')
    user = os.environ.get('DJANGO_MAIL_USER')
    pwrd = os.environ.get('DJANGO_MAIL_PWRD')
    recipients = os.environ.get('DJANGO_MAIL_ADMIN')
    api_url = api_host + '/api/tasks/check_background_services/?format=json'
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    timer_interval_sec = int(os.environ.get('DJANGO_SERVICE_INTERVAL_SEC'))
    started = True
    while True:
        try:
            extra_param = ''
            if started:
                extra_param = '&started=true'
            resp = requests.get(api_url + extra_param, headers=headers, verify=verify)
            if started:
                started = False
                console_log('started')
            else:
                console_log('work')
        
            if (resp.status_code != 200):
                try:
                    content_str = resp.content.decode()
                except (UnicodeDecodeError, AttributeError):
                    content_str = resp.content
                subtype = 'plain'
                if '<html' in content_str:
                    subtype = 'html'
                notify(mail_host, user, pwrd, recipients, '[x] error ' + str(resp.status_code), content_str, maintype='text', subtype=subtype)
            else:
                data_str = resp.json()
                data = json.loads(data_str)
                status = '[x] unexpected response'
                if ('result' in data):
                    status = data['result']
                if (status != 'ok'):
                    info = json.dumps(data)
                    notify(mail_host, user, pwrd, recipients, status, info)
        except Exception as ex:
            subtype = 'plain'
            if '<html' in str(ex):
                subtype = 'html'
            notify(mail_host, user, pwrd, recipients, '[x] exception', str(ex), maintype='text', subtype=subtype)
        time.sleep(timer_interval_sec)