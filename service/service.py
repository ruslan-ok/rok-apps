"""Site service

A service for checking tasks that require reminders and for collecting statistics on site visits."""
import time, os, errno, sys, smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from secret import log_path, timer_interval_sec, mail_login, mail_pass, mail_from, mail_to
from logs import ripe as stat_ripe, process as stat_process
from todo import ripe as todo_ripe, process as todo_process
from fuel import process as fuel_process

class Checker():

    def send_mail(self, info):
        s = smtplib.SMTP(host='rusel.by', port=25)
        s.starttls()
        s.login(mail_login, mail_pass)
        msg = EmailMessage()
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Subject']='Notificator info'
        msg.set_content(info)
        s.send_message(msg)
        del msg
        s.quit()

    def log(self, info, send_mail=False):
        if send_mail:
            self.send_mail(info)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        dt_now = datetime.now()
        pref = log_path + dt_now.strftime('%Y/%m/%d_')
        filename = pref + 'service.log'
        
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                            
        with open(filename, 'a') as f:
            f.write(dt_now.strftime('%H:%M:%S') + '   ' + info + '\n')
        print(dt_now.strftime('%H:%M:%S') + '   ' + info)

    def start(self):
        self.log('Started')

    def check(self, fuel_check):
        ret = False
        try:
            if stat_ripe():
                stat_process(self.log)
            if todo_ripe(self.log):
                todo_process(self.log)
            if fuel_check:
                ret = fuel_process(self.log)
        except Exception as e:
            self.log('[x] Checker.check() [service.py] Exception: ' + str(e)) #str(sys.exc_info()[0]))
        return ret

if (__name__ == '__main__'):
    checker = Checker()
    checker.start()
    last_log = None
    last_fuel_check = None
    fuel_check = False
    while True:
        if not last_fuel_check or ((datetime.now() - last_fuel_check) >= timedelta(hours=24)):
            last_fuel_check = datetime.now()
            fuel_check = True
        if checker.check(fuel_check):
            fuel_check = False
        time.sleep(timer_interval_sec)
        if not last_log or ((datetime.now() - last_log) >= timedelta(hours=1)):
            last_log = datetime.now()
            checker.log('[i] Service is working.')
