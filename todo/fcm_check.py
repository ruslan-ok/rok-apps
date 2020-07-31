import sys
import time
from datetime import datetime, timedelta
import requests
from secret import url, cacert, timer_interval_sec, check_interval_sec, log_path

class Checker():
    def __init__(self):
        self.last_write = None

    def log(self, info):
        dt_now = datetime.now()
        now = str(dt_now)
        pref = log_path + dt_now.strftime('%Y-%m-%d_')
        with open(pref + 'reminder.log', 'a') as f:
            f.write(dt_now.strftime('%H:%M:%S') + '   ' + info + '\n')
        print(now + '   ' + info)

    def start(self):
        self.qty = 0
        self.log('Started')
        self.last_write = datetime.now()

    def check(self):
        self.qty += 1
        now = datetime.now()
        delta = timedelta(seconds = check_interval_sec)
        if ((now - self.last_write) >= delta):
            self.log('check: delta = ' + str((now - self.last_write).seconds) + ', qty = ' + str(self.qty))
            self.last_write = datetime.now()
            self.qty = 0

        try:
            response = requests.get(url, verify = cacert)
            if (response.status_code != 200) or (response.content != b'ok'):
                self.log('response: code = {}, content = {}'.format(response.status_code, response.content.decode('utf-8')))
        except:
            self.log('[x] Exception: ' + str(sys.exc_info()[0]))

if __name__ == '__main__':
    checker = Checker()
    checker.start()
    while True:
        checker.check()
        time.sleep(timer_interval_sec)
