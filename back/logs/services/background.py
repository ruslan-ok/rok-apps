import os
from datetime import datetime
from logs.service_log import ServiceLog
from logs.models import EventType

class BackgroundLogData(ServiceLog):
    template_name = 'background'

    def __init__(self):
        this_device = os.environ.get('DJANGO_DEVICE')
        super().__init__(this_device, 'cron', 'worker')
        self.local_log = True

    def get_extra_context(self, request):
        context = {}
        day = datetime.today().date()
        if 'day' in request.GET:
            day = datetime.strptime(request.GET['day'], '%Y%m%d')
        context['events'] = self.get_events(device=self.dev, app=self.app, service=self.svc, day=day)

        if self.get_health():
            context['status'] = 'work'
            context['status_color'] = '#12AD2B'
        else:
            context['status'] = 'stoped'
            context['status_color'] = 'red'
        return context

    def get_health(self):
        last_start = None
        last_call = None
        start_events = self.get_events(device=self.dev, app=self.app, service=self.svc, type=EventType.INFO, name='start')
        call_events = self.get_events(device=self.dev, app=self.app, service=self.svc, type=EventType.INFO, name='work')
        if len(call_events) > 0:
            last_call = call_events[0].created
        if len(start_events) > 0:
            last_start = start_events[0].created
            if not last_call or last_call < last_start:
                last_call = last_start
        if last_call:
            sec = (datetime.now() - last_call).total_seconds()
            if sec < 120:
                return True
        return False
