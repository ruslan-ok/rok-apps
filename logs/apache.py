import re

LOG_PATH = 'W:\ssl_request.log'

record_parts = [
    r'\[(?P<time>.+)',     # time %t
    r'(?P<timezone>.+)\]', # timezone %t
    r'(?P<host>\S+)',      # host %h
    r'(?P<prot1>\S+)',     # protocol1 %p
    r'(?P<prot2>\S+)',     # protocol2 %p
    r'"(?P<request>.*)"',  # request "%r"
    r'(?P<size>\S+)',      # size %b (careful, can be '-')
]

request_parts = [
    r'(?P<method>\S+)',   # method
    r'(?P<uri>\S+)',      # uri
    r'(?P<protocol>\S+)', # protocol
]

record_pattern = re.compile(r'\s+'.join(record_parts)+r'\s*\Z')
request_pattern = re.compile(r'\s+'.join(request_parts)+r'\s*\Z')

#'117.50.38.174 - - [01/May/2022:19:50:09 +0300] "GET / HTTP/1.0" 301 225'
#'[01/May/2022:19:17:22 +0300] 178.172.132.29 TLSv1.3 TLS_CHACHA20_POLY1305_SHA256 "GET /en/api/tasks/reminder_ripe/?format=json HTTP/1.1" 16'

if __name__ == '__main__':
    qnt = 0
    with open(LOG_PATH, 'r') as f:
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
                qnt += 1
    print(qnt)
