"""Extracting statistical data about site requests from the Apache server log file.

Parameters
-------------------
apache_log: str
    Path and name of the Apache server log file access.log.
log_sz_file: str
    Path and name of the service file for storing the size of the previously processed log file.

Exported functions:
-------------------
ripe()
process(log)
"""
import re, datetime, requests
from pathlib import Path
from db import DB
from secret import apache_log, log_sz_file

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

def ripe():
    """Whether a new piece of data has appeared in the log file for processing.
    
    Returns
    ----------
    True if a new piece of data is ready for processing.
    """
    prev_log_sz = read_log_sz()
    new_log_sz = Path(apache_log).stat().st_size
    return (new_log_sz > prev_log_sz)

def process(log):
    """Parsing new lines of the log file and saving the received data in the database.
    
    Parameters
    ----------
    log: method
        Method for logging processed data.
    """
    mgr = Manager(log)
    mgr.process()
    mgr.done()

def read_log_sz():
    log_sz = 0
    try:
        with open(log_sz_file, 'r') as f:
            log_sz = int(f.read())
    except FileNotFoundError:
        pass # Acceptable situation - we believe that the log file has not been processed yet
    return log_sz
    
def save_log_sz(log_sz):
    with open(log_sz_file, 'w') as f:
        f.write(str(log_sz))
    
class Manager():
    def __init__(self, log):
        self.log = log
        self.db = DB()
        self.db.open()
        self.added_hosts = 0
        self.added_records = 0
        
    def done(self):
        self.log('[LOGS] New log data, bytes: {}, added hosts: {}, log records: {}'.format(self.new_log_sz - self.prev_log_sz, self.added_hosts, self.added_records))
        self.db.close()
        
    def process(self):
        self.prev_log_sz = read_log_sz()
        self.new_log_sz = Path(apache_log).stat().st_size
        save_log_sz(self.new_log_sz)
        with open(apache_log, 'r') as f:
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
        
    
    def del_all_records(self):
        """Deleting ALL RECORDS of the table AccessLog.
        
        This method is used for testing purposes only."""
        self.db.execute('DELETE FROM %d.hier_accesslog')
        print('Table AccessLog cleared')
        
    def del_all_hosts(self):
        """Deleting ALL RECORDS of the table IPInfo.
        
        This method is used for testing purposes only."""
        self.db.execute('DELETE FROM %d.hier_ipinfo')
        print('Table IPInfo cleared')
        
    def get_host(self, host):
        ret = self.db.execute('SELECT id FROM %d.hier_ipinfo WHERE ip = ?', (host,))
        ip = None
        if ret and ret[0] and (len(ret[0]) > 0):
            ip = ret[0][0]
        return ip
    
    def add_host(self, host):
        data = get_host_info(host)
    
        if not 'counrty_code' in data:
            self.db.execute('INSERT INTO %d.hier_ipinfo (ip, success) VALUES (?, ?)', (host, False))
        else:
            params = (data['ip'], data['success'], data['type'], data['continent'], data['continent_code'], data['country'], data['country_code'],
                 data['country_flag'], data['country_capital'], data['country_phone'], data['country_neighbours'], data['region'],
                 data['city'], data['latitude'], data['longitude'], data['asn'], data['org'], data['timezone_dstOffset'], data['timezone_gmtOffset'],
                 data['timezone_gmt'], data['currency'], data['currency_code'], data['currency_symbol'])
            fields = """ip, success, ip_type, continent, continent_code, country, country_code, country_flag, country_capital, 
                        country_phone, country_neighbours, region, city, latitude, longitude, asn, org, timezone_dstOffset,
                        timezone_gmtOffset, timezone_gmt, currency, currency_code, currency_symbol"""
            ph = '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?'
            self.db.execute('INSERT INTO %d.hier_ipinfo ({}) VALUES ({})'.format(fields, ph), params)
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
        
        params = (host_id, user, datetime.datetime.strptime(time, '%d/%b/%Y:%H:%M:%S'), method, uri, protocol, status, size)
        self.db.execute('INSERT INTO %d.hier_accesslog (host_id, user, event, method, uri, protocol, status, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', params)
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

    if not data['success']:
        print('Bad response for host ' + host, data)
        data = {'ip': host}

    return data
        
    