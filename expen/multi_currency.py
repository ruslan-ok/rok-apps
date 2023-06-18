from datetime import datetime
from task.models import Task

def multi_currency_init():
    total = byr = byn = usd = eur = gbp = undef = conflict = upd = ins = 0
    undef_ids = []
    conflict_ids = []
    for t in Task.objects.exclude(app_expen=0):
        total += 1
        sums = []
        if t.expen_price:
            if not t.event:
                undef += 1
                undef_ids.append(t.id)
            else:
                if t.event < datetime(2016, 6, 1):
                    byr += 1
                    sums.append((t.expen_price, 'BYR'))
                else:
                    byn += 1
                    sums.append((t.expen_price, 'BYN'))
        if t.expen_usd:
            usd += 1
            sums.append((t.expen_usd, 'USD'))
        if t.expen_eur:
            eur += 1
            sums.append((t.expen_eur, 'EUR'))
        if t.expen_gbp:
            gbp += 1
            sums.append((t.expen_gbp, 'GBP'))
        if len(sums) > 1:
            conflict += 1
            conflict_ids.append(t.id)
        if len(sums) > 0 and not t.price_unit:
            for i, s in enumerate(sums):
                if i == 0:
                    upd += 1
                else:
                    ins += 1
                    t.pk = None
                t.expen_price = s[0]
                t.price_unit = s[1]
                t.save()
    return {'result': 'ok', 'total': total, 'byr': byr, 'byn': byn, 'usd': usd, 'eur': eur, 'gbp': gbp, 'undef': undef, 'undef_ids': undef_ids, 'conflict': conflict, 'conflict_ids': conflict_ids, 'ins': ins, 'upd': upd}

