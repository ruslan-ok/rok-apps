"""Module for interacting with the SQLite database"""
import requests, json, datetime, sqlite3, mysql.connector
from secret import use_mysql, db_file, host, user, password, database, auth_plugin

class DB():
    def open(self):
        if use_mysql:
            self.con = mysql.connector.connect(host=host, user=user, password=password, database=database, auth_plugin=auth_plugin)
        else:
            self.con = sqlite3.connect(db_file)
        self.added_hosts = 0
        self.added_records = 0
        if use_mysql:
            self.param_ph = '%s'
        else:
            self.param_ph = '?'

    def close(self):
        self.con.commit()
        self.con.close()

    def get_cursor(self):
        if use_mysql:
            return self.con.cursor(buffered=True)
        else:
            return self.con.cursor()

    def del_all_records(self):
        """Deleting ALL RECORDS of the table AccessLog.
        
        This method is used for testing purposes only."""
        cur = self.get_cursor()
        cur.execute('DELETE FROM hier_accesslog')
        print('Table AccessLog cleared')
        
    def del_all_hosts(self):
        """Deleting ALL RECORDS of the table IPInfo.
        
        This method is used for testing purposes only."""
        cur = self.get_cursor()
        cur.execute('DELETE FROM hier_ipinfo')
        print('Table IPInfo cleared')
        
    def get_host(self, host):
        cur = self.get_cursor()
        t = (host,)
        cur.execute('SELECT id FROM hier_ipinfo WHERE ip = {}'.format(self.param_ph), t)
        ret = cur.fetchone()
        ip = None
        if ret and (len(ret) > 0):
            ip = ret[0]
        return ip
    
    def get_host_info(self, host):
        if (datetime.date.today() < datetime.date(2021, 4, 18)):
            # Bad response for host 125.25.204.84 {'success': False, 'message': "you've hit the monthly limit"}
            return {'ip': host}

        resp = requests.get('http://ipwhois.app/json/' + host)
        info = resp.content.decode('utf-8')
        data = resp.json()

        if not data['success']:
            print('Bad response for host ' + host, data)
            data = {'ip': host}

        return data
        
    def get_values_ph(self, num):
        values_ph = ''
        for i in range(num-1):
            values_ph += '{}, '.format(self.param_ph)
        values_ph += '{}'.format(self.param_ph)
        return values_ph

    def add_host(self, host):
        cur = self.get_cursor()
        data = self.get_host_info(host)

        if not 'counrty_code' in data:
            param = (host,)
            request = 'INSERT INTO hier_ipinfo (ip) VALUES ({})'.format(self.param_ph)
            print(request, param)
            cur.execute(request, param)
        else:
            param = (data['ip'], data['success'], data['type'], data['continent'], data['continent_code'], data['country'], data['country_code'],
                 data['country_flag'], data['country_capital'], data['country_phone'], data['country_neighbours'], data['region'],
                 data['city'], data['latitude'], data['longitude'], data['asn'], data['org'], data['timezone_dstOffset'], data['timezone_gmtOffset'],
                 data['timezone_gmt'], data['currency'], data['currency_code'], data['currency_symbol'],)
            try:
                fields = """ip, success, ip_type, continent, continent_code, country, country_code, country_flag, country_capital, 
                            country_phone, country_neighbours, region, city, latitude, longitude, asn, org, timezone_dstOffset,
                            timezone_gmtOffset, timezone_gmt, currency, currency_code, currency_symbol"""
                cur.execute('INSERT INTO hier_ipinfo ({}) VALUES ({})'.format(fields, self.get_values_ph(23)), param)
            except sqlite3.IntegrityError:
                print('sqlite3.IntegrityError:', param)
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
        
        param = (host_id, user, datetime.datetime.strptime(time, '%d/%b/%Y:%H:%M:%S'), method, uri, protocol, status, size)
        
        cur = self.get_cursor()
        fields = 'host_id, user, event, method, uri, protocol, status, size'
        cur.execute('INSERT INTO hier_accesslog ({}) VALUES ({})'.format(fields, self.get_values_ph(8)), param)
        self.added_records += 1
    
    def save_log_record(self, record):
        if 'host' in record:
            host_id = self.save_host(record['host'])
            self.save_record(host_id, record)


