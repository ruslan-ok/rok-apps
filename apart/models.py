from datetime import datetime, date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.urls import reverse

from .utils import get_new_period
from hier.files import get_files_list


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

    class Meta:
        verbose_name = _('apartment')
        verbose_name_plural = _('apartments')

    def __str__(self):
        return self.name

    def get_info(self):
        ret = []
        ret.append({'text': self.addr })
        return ret

    def marked_item(self):
        return self.active

    def s_active(self):
        if self.active:
            return '*'
        else:
            return ''

    def get_absolute_url(self):
        return reverse('apart:apart_form', args = ['0', str(self.id)])

def deactivate_all(user_id, apart_id):
    for apart in Apart.objects.filter(user = user_id, active = True).exclude(id = apart_id):
        apart.active = False
        apart.save()

def set_active(user_id, apart_id):
    if Apart.objects.filter(user = user_id, id = apart_id).exists():
        apart = Apart.objects.filter(user = user_id, id = apart_id).get()
        deactivate_all(user_id, apart.id)
        apart.active = True
        apart.save()


#----------------------------------
# Meter

class Meter(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, verbose_name = _('apartment'))
    period = models.DateField(_('period'), default = get_new_period)
    reading = models.DateTimeField(_('meters reading date'), default = datetime.now)
    el = models.IntegerField(_('electricity'), null = True)
    hw = models.IntegerField(_('hot water'), null = True)
    cw = models.IntegerField(_('cold water'), null = True)
    ga = models.IntegerField(_('gas'), null = True)
    zhirovka = models.DecimalField('account amount', null = True, blank = True, max_digits = 15, decimal_places = 2)
    info = models.CharField(_('information'), max_length = 1000, blank = True)

    class Meta:
        verbose_name = _('meters data')
        verbose_name_plural = _('meters data')

    def __str__(self):
        ret = self.period.strftime('%m.%Y') + ' el: ' + str(self.el) + ', hw: ' + str(self.hw) + ', cw: ' + str(self.cw)
        if (self.apart.has_gas):
            ret += ', ga: ' + str(self.ga)
        return ret

    def name(self):
        return self.period.strftime('%m.%Y')

    def get_info(self):
        ret = []
        ret.append({'text': '{} {}'.format(_('el:'), self.el)})
        ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('hw:'), self.hw)})
        ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('cw:'), self.cw)})
        if (self.apart.has_gas):
            ret.append({'icon': 'separator'})
            ret.append({'text': '{} {}'.format(_('ga:'), self.ga)})
        return ret


#----------------------------------
# Bill

class Bill(models.Model):
    apart = models.ForeignKey(Apart, on_delete = models.CASCADE, verbose_name = _('apartment'))
    period = models.DateField(_('period'), default = get_new_period)
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

    def total_usd(self):
        if (self.rate == 0) or (not self.rate):
            return 0
        else:
            return int(self.total_bill() / round(self.rate, 0))

    def el_vol(self):
        return self.curr.el - self.prev.el
  
    def gs_vol(self):
        return self.curr.ga - self.prev.ga
  
    def wt_vol(self):
        return (self.curr.hw + self.curr.cw) - (self.prev.hw + self.prev.cw)
  
    def total_bill(self):
        bill = count_by_tarif(self.apart.id, self.prev, self.curr, ELECTRICITY) + \
               count_by_tarif(self.apart.id, self.prev, self.curr, GAS) + \
               count_by_tarif(self.apart.id, self.prev, self.curr, WATER) + \
               count_by_tarif(self.apart.id, self.prev, self.curr, WATER_SUPPLY) + \
               count_by_tarif(self.apart.id, self.prev, self.curr, SEWERAGE) + \
               zero(self.tv_bill) + zero(self.phone_bill) + zero(self.zhirovka) + zero(self.PoO)
        return round(bill, 2)

    def total_pay(self):
        return zero(self.tv_pay) + zero(self.phone_pay) + zero(self.hot_pay) + zero(self.repair_pay) + zero(self.ZKX_pay) + zero(self.el_pay) + zero(self.water_pay) + zero(self.gas_pay) + zero(self.PoO_pay)

    def debt(self):
        return int(round(self.total_bill(), 0)) - self.total_pay()

    def name(self):
        return self.period.strftime('%m.%Y')

    def get_info(self):
        ret = []

        ret.append({'text': '{}: {}'.format(_('total bill'), self.total_bill()) })
        ret.append({'icon': 'separator'})
        ret.append({'text': '{}: {}'.format(_('total pay'), self.total_pay()) })
    
        files = get_files_list(self.apart.user, app_name, 'apart_{}/{}/{}'.format(self.apart.id, self.period.year, str(self.period.month).zfill(2)))
    
        if self.url or self.info or len(files):
            ret.append({'icon': 'separator'})
    
        if self.url:
            ret.append({'icon': 'url'})
    
        if self.info:
            ret.append({'icon': 'notes'})
    
        if len(files):
            ret.append({'icon': 'attach'})
    
        return ret
        

def zero(value):
    if value:
        return value
    else:
        return 0
    
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

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        return self.name

    def get_info(self):
        ret = []
        if (self.abbr == ELECTRICITY) or (self.abbr == GAS) or (self.abbr == WATER):
            ret.append({'icon': 'separator'})
        ret.append({'text': self.abbr})
        return ret
        
def get_serv_id(apart_id, service_id):
    if Service.objects.filter(apart = apart_id, abbr = service_id).exists():
        service = Service.objects.filter(apart = apart_id, abbr = service_id).get()
        return service.id
    return None

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

    class Meta:
        verbose_name = _('tariff')
        verbose_name_plural = _('tariffs')

    def __str__(self):
        b1 = self.border
        if not b1:
            b1 = 0

        t1 = self.tarif
        if not t1:
            t1 = 0

        b2 = self.border2
        if not b2:
            b2 = 0

        t2 = self.tarif2
        if not t2:
            t2 = 0

        t3 = self.tarif3
        if not t3:
            t3 = 0

        if (b1 == 0):
            ret = str(t1)
        else:
            ret = str(t1) + ' ' + gettext('until') + ' ' + str(b1) + ' / ' + str(t2)
      
        if (b2 != 0):
            ret += ' ' + gettext('until') + ' ' + str(b2) + ' / ' + str(t3)
        return ret

    def s_service(self):
        if (len(self.service) < 2):
            return _('unknown')
        return SERVICE_STR[self.service]

    def name(self):
        return self.start.strftime('%d.%m.%Y')

    def get_info(self):
        b1 = self.border
        if not b1:
            b1 = 0

        t1 = self.tarif
        if not t1:
            t1 = 0

        b2 = self.border2
        if not b2:
            b2 = 0

        t2 = self.tarif2
        if not t2:
            t2 = 0

        t3 = self.tarif3
        if not t3:
            t3 = 0

        p1 = ''
        p2 = ''
        p3 = ''

        if (b1 == 0):
            p1 = str(t1)
        else:
            p1 = '{:.3f} {} {:.0f} {}'.format(t1, gettext('until'), b1, self.unit)
            if (b2 == 0):
                p2 = '{:.3f}'.format(t2)
            else:
                p2 = '{:.3f} {} {:.0f} {}'.format(t2, gettext('until'), b2, self.unit)
                p3 = '{:.3f}'.format(t3)
    
        ret = []
        if p1:
            ret.append({'text': p1})
        if p2:
            ret.append({'icon': 'separator'})
            ret.append({'text': p2})
        if p3:
            ret.append({'icon': 'separator'})
            ret.append({'text': p3})
        return ret
  
def get_price_info(apart_id, service_id, year, month):
    serv_id = get_serv_id(apart_id, service_id)
    period = date(year, month, 1)
    prices = Price.objects.filter(apart = apart_id, serv = serv_id, start__lte = period).order_by('-start')[:1]
    if (len(prices) == 0):
        return ''
    else:
        return str(prices[0])
    
#----------------------------------
def get_per_price(apart_id, service_id, year, month):
    ret = {'t1': 0,
           'b1': 0,
           't2': 0,
           'b2': 0,
           't3': 0}

    tarifs = Price.objects.filter(apart = apart_id,
                                  serv = get_serv_id(apart_id, service_id),
                                  start__lte = date(year, month, 1)).order_by('-start')[:1]
    if (len(tarifs) > 0):
      
        if tarifs[0].tarif:
            ret['t1'] = tarifs[0].tarif
        else:
            ret['t1'] = 0
      
        if tarifs[0].border:
            ret['b1'] = tarifs[0].border
        else:
            ret['b1'] = 0
      
        if tarifs[0].tarif2:
            ret['t2'] = tarifs[0].tarif2
        else:
            ret['t2'] = 0
      
        if tarifs[0].border2:
            ret['b2'] = tarifs[0].border2
        else:
            ret['b2'] = 0
      
        if tarifs[0].tarif3:
            ret['t3'] = tarifs[0].tarif3
        else:
            ret['t3'] = 0
  
    return ret

def count_by_tarif(apart_id, prev, curr, service_id):

    vol = 0
    if (service_id == ELECTRICITY):
        vol = curr.el - prev.el
    elif (service_id == GAS) and curr.ga and prev.ga:
        vol = curr.ga - prev.ga
    elif (service_id == WATER) or (service_id == WATER_SUPPLY) or (service_id == SEWERAGE):
        vol = (curr.hw + curr.cw) - (prev.hw + prev.cw)

    tar = get_per_price(apart_id, service_id, curr.period.year, curr.period.month)

    if (tar['b1'] == 0) or (vol <= tar['b1']):
        return vol * tar['t1']
    else:
        i_sum = tar['b1'] * tar['t1']
        if (tar['b2'] == 0) or (vol <= tar['b2']):
            return i_sum + (vol - tar['b1']) * tar['t2']
        else:
            return i_sum + (tar['b2'] - tar['b1']) * tar['t2'] + (vol - tar['b2']) * tar['t3']




