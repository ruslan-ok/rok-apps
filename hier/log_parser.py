import requests, json, collections
from pathlib import Path
from datetime import datetime, timezone
from django.utils.translation import gettext_lazy as _
from .secret import log_name
from .models import IPInfo, LogRecord, ActDetect

def start_log_parser():
    """Parse Apache ssl_request.log"""
    TOTAL_LOG = _('total log records').capitalize()
    TOTAL_IP = _('total different').capitalize() + ' IP'
    NEW_LOG = _('new log records').capitalize()
    NEW_IP = _('new').capitalize() + ' IP'
 
    last = log_sz = last_pos = None
    last_event = datetime.min
    if LogRecord.objects.exists():
        last = LogRecord.objects.order_by('-event')[0]
        last_event = last.event
        last_pos = last.log_sz
    cnt = collections.Counter()
    log_sz = Path(log_name).stat().st_size
    stat = {}
    with open(log_name, 'r') as f:
        if last_pos:
            f.seek(last_pos)
        while True:
            sIP = country = prot = crypt = method = addr = vers = ''
            event = size = None
            valid = False
            s = f.readline()
            if not s:
                break
            if (s == '\n'):
                break
            sdt = s.split('] ')[0].replace('[', '')
            event = datetime.strptime(sdt, '%d/%b/%Y:%H:%M:%S %z').astimezone(tz=timezone.utc).replace(tzinfo=None)
            if last_event and (event <= last_event):
                continue
            tails = s.split('] ')[1].split()
            if (tails[1] not in ('TLSv1.3', 'TLSv1.2', 'TLSv1.1', 'TLSv1', '-')):
                stat['error_1'] = (tails[1], tails)
                break
            sIP = tails[0]
            prot = tails[1]
            if (tails[2] != '-'):
                if ('-' in tails[2]):
                    algs = tails[2].split('-')
                else:
                    algs = tails[2].split('_')
                check = list(filter(lambda x: x not in ('256', 'AES', 'AES128', 'AES256', 'DHE', 'ECDHE', 'GCM', 'RSA', 'SHA', 'SHA256', 'SHA384', 'TLS'), algs))
                if check:
                    stat['error_2'] = (check, tails[2], tails)
                    break
                prot = tails[2]
                if (tails[3] not in ('"GET', '"POST', '"HEAD', '"OPTIONS', '"SSTP_DUPLEX_POST', '"\\n"', '"-"')):
                    stat['error_3'] = (tails[3], tails)
                    break
                method = tails[3].replace('"', '')
                if (tails[3] in ('"\\n"', '"-"')):
                    if (tails[4] != '-'):
                        size = int(tails[4])
                        if not size:
                            stat['error_4'] = (size, tails)
                            break
                else:
                    addr = tails[4]
                    vers = tails[5].replace('"', '')
                    if (tails[6] != '-'):
                        size = int(tails[6])
                        if not size:
                            stat['error_5'] = (size, tails)
                            break
                    check = tails[4].replace('/ru/', '/').replace('/en/', '/')
                    if (check[-1] != '"') and (check != '-') and (check != '/') and (check != '/?') and (len(check) < 3):
                        stat['error_6'] = (tails[4], tails)
                        break
            valid = False
            if IPInfo.objects.filter(ip = sIP).exists():
                ip = IPInfo.objects.filter(ip = sIP).get()
            else:
                resp = requests.get('http://ipwhois.app/json/' + sIP)
                info = resp.content.decode('utf-8')
                try:
                    data = resp.json()
                    country = data['country_code']
                except json.JSONDecodeError:
                    pass
                ip = IPInfo.objects.create(ip = sIP, country = country, info = info)
                cnt[NEW_IP] += 1
            if addr:
                test = addr.replace('/ru/', '/').replace('/en/', '/')
                valid = (test[:6] == '/todo/') or (test[:6] == '/note/') or (test[:6] == '/news/') or (test[:7] == '/store/') or (test[:6] == '/proj/') or \
                        (test[:6] == '/trip/') or (test[:6] == '/fuel/') or (test[:7] == '/apart/') or (test[:6] == '/wage/') or (test[:7] == '/photo/') or \
                        (test[:8] == '/helth/') or (test[:6] == '/account/') 
            LogRecord.objects.create(ip = ip, event = event, prot = prot, crypt = crypt, method = method, addr = addr, vers = vers, size = size, valid = valid)
            cnt[NEW_LOG] += 1

    recs = LogRecord.objects.filter(valid=True, event__gt=last_event).order_by('addr')
    cur_addr = ''
    for rec in recs:
        if (rec.ip.ip in ('178.172.132.29', '86.57.135.53')): # or ((rec.ip.ip[:11] >= '46.216.128.') and (rec.ip.ip[:11] <= '46.216.255.')):
        #                 rusel.by          topsoft.by                              mts.by
            continue
        if (cur_addr == rec.addr):
            stat[cur_addr] += rec.ip.country + ' ' + rec.ip.ip,
        else:
            cur_addr = rec.addr
            iii = rec.ip.info
            jsn = json.loads(iii)
            act = ActDetect.objects.create(event = rec.event, addr = rec.addr, ip = rec.ip.ip, country = rec.ip.country, org = jsn['org'])
            stat[cur_addr] = (str(act),)
    #stat['/debug-1/'] = ('RU 100.200.300.400 Organization-1', 'UA 1.2.3.4 Organization-1', 'TR 111.222.333.444 Organization-3')
    #stat['/debug-2/'] = ('BY 500.600.700.800 Organization-4', 'UK 5.6.7.8 Organization-5', 'US 555.666.777.888 Organization-6')

    cnt[TOTAL_LOG] = len(LogRecord.objects.all())
    cnt[TOTAL_IP] = len(IPInfo.objects.all())

    return cnt.most_common(), stat
