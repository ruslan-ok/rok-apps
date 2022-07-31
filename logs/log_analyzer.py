"""Extracting statistical data about site requests from the Apache server log file.

Parameters
-------------------
apache_log: str
    Path and name of the Apache server log file access.log.

Exported functions:
-------------------
ripe()
process(log)
"""
import os, re, datetime, requests
from pathlib import Path
from service.site_service import SiteService
from task.const import APP_LOGS
from task.models import ServiceEvent
from logs.models import IPInfo, AccessLog


record_parts = [
    r'(?P<host>\S+)',      # host %h
    r'-',                  # indent %l (unused)
    r'(?P<user>\S+)',      # user %u
    r'\[(?P<time>.+)',     # time %t
    r'(?P<timezone>.+)\]', # timezone %t
    r'"(?P<request>.*)"',  # request "%r"
    r'(?P<status>\d+)',    # status %>s
    r'(?P<size>\S+)',      # size %b (careful, can be '-')
]

request_parts = [
    r'(?P<method>\S+)',   # method
    r'(?P<uri>\S+)',      # uri
    r'(?P<protocol>\S+)', # protocol
]

record_pattern = re.compile(r'\s+'.join(record_parts)+r'\s*\Z')
request_pattern = re.compile(r'\s+'.join(request_parts)+r'\s*\Z')

class LogAnalyzer(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_LOGS, 'logs', *args, **kwargs)
        self.apache_log = os.environ.get('APACHE_LOG')

    def read_log_sz(self):
        log_sz = 0
        log_sz_events = ServiceEvent.objects.filter(app=APP_LOGS, service='log_analyze', type='info', name='log_size').order_by('-created')
        if len(log_sz_events) > 0:
            log_sz = int(log_sz_events[0].info)
        return log_sz

    def ripe(self):
        """Whether a new piece of data has appeared in the log file for processing.
        
        Returns
        ----------
        True if a new piece of data is ready for processing.
        """
        self.prev_log_sz = self.read_log_sz()
        try:
            self.new_log_sz = Path(self.apache_log).stat().st_size
            ret = (self.new_log_sz > self.prev_log_sz)
        except:
            ret = False
        # self.log_event('debug', 'ripe', 'result = ' + str(ret))
        return ret

    def process(self):
        """Parsing new lines of the log file and saving the received data in the database.
        """
        self.added_hosts = 0
        self.added_records = 0
        self.log_event('info', 'log_size', str(self.new_log_sz))
        with open(self.apache_log, 'r') as f:
            if self.prev_log_sz:
                f.seek(self.prev_log_sz)
            while True:
                line = f.readline()
                if not line:
                    break
                re_data = record_pattern.match(line)
                if not re_data:
                    print(line)
                else:
                    data = re_data.groupdict()
                    s_request = data['request']
                    re_request = request_pattern.match(s_request)
                    if re_request:
                        request = re_request.groupdict()
                        data.update(request)
                        
                    self.save_log_record(data)
        self.log_event('info', 'new_data', 'bytes: {}, added hosts: {}, log records: {}'.format(self.new_log_sz - self.prev_log_sz, self.added_hosts, self.added_records))

    def get_host(self, host):
        if IPInfo.objects.filter(ip=host).exists():
            return IPInfo.objects.filter(ip=host).get().ip
        return None
    
    def add_host(self, host):
        data = get_host_info(host)
    
        if not 'success' in data or not data['success']:
            self.log_event('error', 'bad_response', 'Bad response for host ' + host)
            data = {'ip': host}

        if not 'counrty_code' in data:
            IPInfo.objects.create(ip=host, success=False)
        else:
            IPInfo.objects.create(
                ip=data['ip'],
                success=data['success'],
                ip_type=data['type'],
                continent=data['continent'],
                continent_code=data['continent_code'],
                country=data['country'],
                country_code=data['country_code'],
                country_flag=data['country_flag'],
                country_capital=data['country_capital'],
                country_phone=data['country_phone'],
                country_neighbours=data['country_neighbours'],
                region=data['region'],
                city=data['city'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                asn=data['asn'],
                org=data['org'],
                timezone_dstOffset=data['timezone_dstOffset'],
                timezone_gmtOffset=data['timezone_gmtOffset'],
                timezone_gmt=data['timezone_gmt'],
                currency=data['currency'],
                currency_code=data['currency_code'],
                currency_symbol=data['currency_symbol'],
                )
        self.added_hosts += 1
        return self.get_host(host)
    
    def save_host(self, host):
        host_id = self.get_host(host)
        if host_id:
            return host_id
        return self.add_host(host)
    
    def save_record(self, host_id, record):
        user = record['user']
        time = record['time']
        if 'method' in record:
            method = record['method']
            uri = record['uri']
            protocol = record['protocol']
        else:
            method = protocol = ''
            uri = record['request']
    
        status = size = 0
    
        if int(record['status']):
            status = int(record['status'])
        
        if (record['size'] != '-'):
            size = int(record['size'])
        
        AccessLog.objects.create(
            host_id=host_id,
            user=user,
            event=datetime.datetime.strptime(time, '%d/%b/%Y:%H:%M:%S'),
            method=method,
            uri=uri,
            protocol=protocol,
            status=status,
            size=size,
            )
        self.added_records += 1
    
    def save_log_record(self, record):
        if 'host' in record:
            host_id = self.save_host(record['host'])
            self.save_record(host_id, record)

def get_host_info(host):
    if (datetime.date.today() < datetime.date(2021, 4, 18)):
        # Bad response for host x.x.x.x {'success': False, 'message': "you've hit the monthly limit"}
        return {'ip': host}

    resp = requests.get('http://ipwhois.app/json/' + host)
    info = resp.content.decode('utf-8')
    data = resp.json()
    return data
