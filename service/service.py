"""Site service

A service for checking tasks that require reminders and for collecting statistics on site visits."""
import time, os, errno, sys
from datetime import datetime
from secret import log_path, timer_interval_sec
from logs import ripe as stat_ripe, process as stat_process
from todo import ripe as todo_ripe, process as todo_process

class Checker():
    def log(self, info):
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

    def check(self):
        try:
            if stat_ripe():
                stat_process(self.log)
            if todo_ripe():
                todo_process(self.log)
        except:
            self.log('[x] Checker.check() [service.py] Exception: ' + str(sys.exc_info()[0]))

if (__name__ == '__main__'):
    checker = Checker()
    checker.start()
    while True:
        checker.check()
        time.sleep(timer_interval_sec)
