from datetime import datetime
from logs.log_data.log_data import LogData
from task.models import ServiceEvent

class BackgroundLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app='service', service='manager').order_by('-created')

        status = 'stoped'
        color = 'red'
        last_start = None
        last_call = None
        start_events = ServiceEvent.objects.filter(app='service', service='manager', type='info', name='start').order_by('-created')
        call_events = ServiceEvent.objects.filter(app='service', service='manager', type='info', name='call').order_by('-created')
        if len(call_events) > 0:
            last_call = call_events[0].created
        if len(start_events) > 0:
            last_start = start_events[0].created
            if not last_call or last_call < last_start:
                last_call = last_start
        if last_call:
            sec = (datetime.now() - last_call).total_seconds()
            if sec < 120:
                status = 'work'
                color = '#12AD2B'
        context['status'] = status
        context['status_color'] = color
        return context

