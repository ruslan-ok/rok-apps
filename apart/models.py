from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

app_name = 'apart'

APART = 'aparts'
SERV = 'services'
METER = 'meters'
PRICE = 'prices'
BILL = 'bills'

#----------------------------------
# Apartment

class Apart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name = models.CharField(_('name'), max_length = 1000)
    addr = models.CharField(_('address'), max_length = 5000, blank = True)
    active = models.BooleanField(_('active'), default = False)
    has_gas = models.BooleanField(_('has gas'), default = True)
    has_ppo = models.BooleanField(_('payments to the partnership of owners'), default = False)

#----------------------------------
# Meter

class Meter(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, verbose_name = _('apartment'))
    period = models.DateField(_('period'))
    reading = models.DateTimeField(_('meters reading date'), default = datetime.now)
    el = models.IntegerField(_('electricity'), null = True)
    hw = models.IntegerField(_('hot water'), null = True)
    cw = models.IntegerField(_('cold water'), null = True)
    ga = models.IntegerField(_('gas'), null = True)
    zhirovka = models.DecimalField('account amount', null = True, blank = True, max_digits = 15, decimal_places = 2)
    info = models.CharField(_('information'), max_length = 1000, blank = True)

#----------------------------------
# Bill

class Bill(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, verbose_name = _('apartment'))
    period = models.DateField(_('period'))
    payment = models.DateTimeField(_('date of payment'), default = datetime.now)
    prev = models.ForeignKey(Meter, on_delete = models.CASCADE, verbose_name = _('previous period meters data'), related_name = 'previous')
    curr = models.ForeignKey(Meter, on_delete = models.CASCADE, verbose_name = _('current period meters data'),  related_name = 'current')
    el_pay = models.DecimalField('electro - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    tv_bill = models.DecimalField('tv - accrued', null = True, blank = True, max_digits = 15, decimal_places = 2)
    tv_pay = models.DecimalField('tv - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    phone_bill = models.DecimalField('phone - accrued', null = True, blank = True, max_digits = 15, decimal_places = 2)
    phone_pay = models.DecimalField('phone - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    zhirovka = models.DecimalField('zhirovka', null = True, blank = True, max_digits = 15, decimal_places = 2)
    hot_pay = models.DecimalField('heatenergy - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    repair_pay = models.DecimalField('overhaul - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    ZKX_pay = models.DecimalField('HCS - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    water_pay = models.DecimalField('water - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    gas_pay = models.DecimalField('gas - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    rate = models.DecimalField(_('rate').capitalize(), null = True, blank = True, max_digits = 15, decimal_places = 4)
    info = models.TextField(_('information'), blank = True, default = "")
    url = models.CharField(_('url'), max_length = 2000, blank = True)
    PoO = models.DecimalField('pay to the Partnersheep of Owners - accrued', null = True, blank = True, max_digits = 15, decimal_places = 2)
    PoO_pay = models.DecimalField('pay to the Partnersheep of Owners - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)

#----------------------------------
# Price

ELECTRICITY = 'EL'
GAS = 'GA'
WATER = 'WA'
WATER_SUPPLY = 'WS'
SEWERAGE = 'SE'
TV = 'TV'
INTERNET = 'IN'
PHONE = 'PH'

SERVICE = [
    (ELECTRICITY, _('power supply')),
    (GAS, _('gas supply')),
    (WATER_SUPPLY, _('water supply')),
    (SEWERAGE, _('sewerage')),
    (TV, _('television')),
    (INTERNET, _('internet')),
    (PHONE, _('phone')),
    (WATER, _('water')),
]    

SERVICE_STR = {
    ELECTRICITY: _('power supply'),
    GAS: _('gas supply'),
    WATER_SUPPLY: _('water supply'),
    SEWERAGE: _('sewerage'),
    TV: _('television'),
    INTERNET: _('internet'),
    PHONE: _('phone'),
    WATER: _('water'),
}    

class Service(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, verbose_name = _('apartment'), null = True)
    abbr = models.CharField(_('abbreviation'), max_length = 2)
    name = models.CharField(_('name'), max_length = 100)
    is_open = models.BooleanField(_('node is opened'), default = False)

class Price(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, null = True, verbose_name = _('apartment'))
    serv = models.ForeignKey(Service, on_delete = models.CASCADE, verbose_name = _('service'), null = True)
    start = models.DateField(_('valid from'), default = datetime.now, null = True,  blank = True)
    tarif = models.DecimalField(_('tariff 1'), null = True, blank = False, max_digits = 15, decimal_places = 5)
    border = models.DecimalField(_('border 1'), null = True,  blank = True, max_digits = 15, decimal_places = 4)
    tarif2 = models.DecimalField(_('tariff 2'), null = True,  blank = True, max_digits = 15, decimal_places = 5)
    border2 = models.DecimalField(_('border 2'), null = True,  blank = True, max_digits = 15, decimal_places = 4)
    tarif3 = models.DecimalField(_('tariff 3'), null = True,  blank = True, max_digits = 15, decimal_places = 5)
    info = models.TextField(_('information'), blank=True, default = "")
    unit = models.CharField(_('unit'), max_length = 100, blank = True, null = True)




