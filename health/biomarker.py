import io
from datetime import datetime

from .models import Biomarker

class Markers:
    def __init__(self, height, weight, waist, systolic, diastolic, pulse, temp, info):
        self.height = height
        self.weight = weight
        self.waist = waist
        self.systolic = systolic
        self.diastolic = diastolic
        self.pulse = pulse
        self.temp = temp
        self.info = info

    def __str__(self):
        ret = ''
        if self.height:
            ret = 'height: {}'.format(self.height)
        if self.weight:
            if ret:
                ret += ', '
            ret += 'weight: {}'.format(self.weight)
        if self.waist:
            if ret:
                ret += ', '
            ret += 'waist: {}'.format(self.waist)
        if self.systolic or self.diastolic:
            if ret:
                ret += ', '
            ret += 'pressure: {}/{}'.format(self.systolic, self.diastolic)
        if self.pulse:
            if ret:
                ret += ', '
            ret += 'pulse: {}'.format(self.pulse)
        if self.temp:
            if ret:
                ret += ', '
            ret += 'temp: {}'.format(self.temp)
        if self.info:
            if ret:
                ret += ', '
            ret += 'info: "{}"'.format(self.info)
        return ret

class Parser:

    def not_wt(self, wt, b):
        if b:
            return (b.weight == None)
        return (wt == None)

    def not_tm(self, tm, b):
        if b:
            return (b.temp == None)
        return (tm == None)

    def not_pu(self, pu, b):
        if b:
            return (b.pulse == None)
        return (pu == None)

    def parse_str(self, s, b):
        s = s.strip('"')
        wt = None
        ws = None
        pr = None
        sy = None
        di = None
        pu = None
        tm = None
        info = ''

        save_wt = False
        save_ws = False
        save_pu = False
        save_tm = False
        save_sy = False
        save_di = False

        added_pr = False
        added_sy = False
        last_int = None

        for x in s.split(' '):
            if (x.strip() == '-'):
                continue
            if save_wt:
                save_wt = False
                if self.not_wt(wt, b):
                    wt = float(x.replace(',', '.').rstrip('.'))
                    continue
            if save_ws:
                save_ws = False
                if (not ws):
                    ws = int(x.rstrip(',').rstrip('.'))
                    continue
            if save_pu:
                save_pu = False
                if self.not_pu(pu, b):
                    pu = int(x.rstrip(',').rstrip('.'))
                    continue
            if save_tm:
                save_tm = False
                if self.not_tm(tm, b):
                    try:
                        tm = float(x.replace(',', '.').rstrip('.'))
                        continue
                    except:
                        pass
            if save_sy:
                save_sy = False
                if (not sy):
                    sy = int(x.rstrip(',').rstrip('.'))
                    added_sy = True
                    continue
            if save_di:
                save_di = False
                if (not di):
                    di = int(x.rstrip(',').rstrip('.'))
                    pr = '{}/{}'.format(sy, di)
                    added_pr = True
                    continue
            if (x == 'Давление'):
                save_sy = True
                continue
            if (x == 'на') and added_sy:
                added_sy = False
                save_di = True
                continue
            if (x == 'Вес') or (x == 'вес'):
                save_wt = True
                continue
            if (x == 'Пузо') or (x == 'пузо'):
                save_ws = True
                continue
            if (x == 'Пульс') or (x == 'пульс'):
                save_pu = True
                continue
            if ((x == 'Температура') or (x == 'температура')) and self.not_tm(tm, b):
                save_tm = True
                continue
            if (x == 'у/м') and last_int and self.not_pu(pu, b):
                if last_int and self.not_pu(pu, b):
                    pu = last_int
                    last_int = None
                if pu:
                    continue
            a = x.split('/')
            if (not pr) and (len(a) == 2):
                try:
                    sy = int(a[0])
                    di = int(a[1])
                    if (sy >= 80) and (sy <= 200) and (di >= 40) and (di <= 120):
                        pr = '{}/{}'.format(sy, di)
                        added_pr = True
                        continue
                except:
                    sy = None
                    di = None
            try:
                z = int(x.rstrip(',').rstrip('.'))
                last_int = z
                if added_pr and (z >= 50) and (z <= 200) and self.not_pu(pu, b):
                    pu = z
                    added_pr = False
                    continue
            except:
                pass
            try:
                z = float(x.replace(',', '.').rstrip('.'))
                if (z >= 35) and (z <= 45) and self.not_tm(tm, b):
                    tm = z
                    continue
                if (z >= 60) and (z <= 95) and self.not_wt(wt, b):
                    wt = z
                    continue
            except:
                pass

            if info:
                info += ' '
            info += x
        
        if (not pr) and (not pu) and (not tm) and (not wt) and (not ws) and (not info):
            return None

        return Markers(None, wt, ws, sy, di, pu, tm, info)

    def run(self, user):
        Biomarker.objects.filter(user = user).delete()
        with io.open('c:/xlam/biomarker/biomarker.csv', 'r', encoding='utf-8') as f:
            while True:
                s = f.readline()
                if not s:
                    break
                a = s.split(';')
                if (len(a) != 3):
                    print(s)
                    break
                t = datetime.strptime(a[2], '"%Y-%m-%d %H:%M:%S.%f"\n')
                b1 = self.parse_str(a[0], None)
                b2 = self.parse_str(a[1], b1)
                info = ''
                if b1:
                    if b1.info:
                        info = b1.info
                else:
                    info = a[0].strip('"')

                if b2:
                    if b2.info:
                        if info:
                            info += ' '
                        info += b2.info
                else:    
                    if info:
                        info += ' '
                    info += a[1].strip('"')

                ht = None
                if b1:
                    ht = b1.height
                if b2 and (not ht):
                    ht = b2.height

                wt = None
                if b1:
                    wt = b1.weight
                if b2 and (not wt):
                    wt = b2.weight

                ws = None
                if b1:
                    ws = b1.waist
                if b2 and (not wt):
                    ws = b2.waist

                tm = None
                if b1:
                    tm = b1.temp
                if b2 and (not tm):
                    tm = b2.temp

                sy = None
                if b1:
                    sy = b1.systolic
                if b2 and (not sy):
                    sy = b2.systolic

                di = None
                if b1:
                    di = b1.diastolic
                if b2 and (not di):
                    di = b2.diastolic

                pu = None
                if b1:
                    pu = b1.pulse
                if b2 and (not pu):
                    pu = b2.pulse

                Biomarker.objects.create(user = user, publ = t, height = ht, weight = wt, waist = ws, temp = tm, systolic = sy, diastolic = di, pulse = pu, info = info)

def run_converter(request):
    x = Parser()
    x.run(request.user)
