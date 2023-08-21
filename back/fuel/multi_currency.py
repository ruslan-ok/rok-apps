from datetime import datetime
from task.models import Task
from task.const import NUM_ROLE_FUEL
from fuel.fuel_get_info import get_info as fuel_get_info

def multi_currency_init():
    total = byr = byn = pln = eur = undef = upd = 0
    undef_ids = []
    for t in Task.objects.filter(app_fuel=NUM_ROLE_FUEL):
        total += 1
        prc = None
        if t.fuel_price:
            if not t.event:
                undef += 1
                undef_ids.append(t.id)
            else:
                if t.event < datetime(2016, 6, 1):
                    byr += 1
                    prc = (t.fuel_price, 'BYR')
                elif t.event < datetime(2023, 4, 1):
                    byn += 1
                    prc = (t.fuel_price, 'BYN')
                elif t.event >= datetime(2023, 4, 29) and t.event <= datetime(2023, 5, 4):
                    eur += 1
                    prc = (t.fuel_price, 'EUR')
                else:
                    pln += 1
                    prc = (t.fuel_price, 'PLN')
        if prc and (not t.price_unit or not t.expen_rate_usd):
            upd += 1
            t.fuel_price = prc[0]
            t.price_unit = prc[1]
            if t.event:
                rate, stat = Task.get_exchange_rate(prc[1], t.event)
                if rate['result'] == 'ok':
                    t.expen_rate_usd = rate['rate_usd']
            t.save()
        fuel_get_info(t)
    return {'result': 'ok', 'total': total, 'byr': byr, 'byn': byn, 'pln': pln, 'eur': eur, 'undef': undef, 'undef_ids': undef_ids, 'upd': upd}

