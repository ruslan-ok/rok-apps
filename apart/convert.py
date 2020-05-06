from datetime import date

from .models_old import Tarif, Communal
from .models import Apart, Meter, Price, Bill, ELECTRICITY, GAS, WATER, WATER_SUPPLY, SEWERAGE
from .utils import get_prev_period


#----------------------------------
def convert_old_data(user, apart):
    if Price.objects.all().exists():
        return
    
    for tarif in Tarif.objects.all():
        if (tarif.resource == 1):
            service = ELECTRICITY
        elif (tarif.resource == 2):
            service = GAS
        elif (tarif.resource == 3):
            service = WATER
        elif (tarif.resource == 4):
            service = WATER_SUPPLY
        elif (tarif.resource == 5):
            service = SEWERAGE
        else:
            service = ELECTRICITY

        Price.objects.create(user = user,
                             service = service,
                             period = date(tarif.period // 100, tarif.period % 100, 1),
                             tarif = tarif.tarif,
                             border = tarif.border,
                             tarif2 = tarif.tarif2,
                             border2 = tarif.border2,
                             tarif3 = tarif.tarif3,
                             info = tarif.text)

    for cmnl in Communal.objects.all():
        Meter.objects.create(apart = apart, 
                             period = date(cmnl.period // 100, cmnl.period % 100, 1),
                             reading = cmnl.dCounter,
                             el = cmnl.el_new,
                             hw = cmnl.hot_new,
                             cw = cmnl.cold_new,
                             ga = cmnl.gas_new)

    for cmnl in Communal.objects.all():
        period = date(cmnl.period // 100, cmnl.period % 100, 1)
        curr = Meter.objects.filter(apart = apart.id, period = period).get()
        prev_per = get_prev_period(period)
        if Meter.objects.filter(apart = apart.id, period = prev_per).exists():
            prev = Meter.objects.filter(apart = apart.id, period = prev_per).get()
        else:
            prev = Meter.objects.create(apart = apart, 
                                        period = prev_per,
                                        reading = cmnl.dCounter,
                                        el = cmnl.el_old,
                                        hw = cmnl.hot_old,
                                        cw = cmnl.cold_old,
                                        ga = cmnl.gas_old)

        Bill.objects.create(apart = apart,
                            period = period,
                            payment = cmnl.dPay,
                            prev = prev,
                            curr = curr,
                            el_pay = cmnl.el_pay,
                            tv_bill = cmnl.tv_tar,
                            tv_pay = cmnl.tv_pay,
                            phone_bill = cmnl.phone_tar,
                            phone_pay = cmnl.phone_pay,
                            zhirovka = cmnl.zhirovka,
                            hot_pay = cmnl.hot_pay,
                            repair_pay = cmnl.repair_pay,
                            ZKX_pay = cmnl.ZKX_pay,
                            water_pay = cmnl.water_pay,
                            gas_pay = cmnl.gas_pay,
                            rate = cmnl.course,
                            info = cmnl.text)

