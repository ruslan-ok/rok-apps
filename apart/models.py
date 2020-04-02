from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from rusel.const import a_months, a_unit
from django.utils.translation import gettext, gettext_lazy as _


class Tarif(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user')) # Пользователь
    res = ((1, _('electro')), (2, _('gas')), (3, _('water')), (4, _('water supply')), (5, _('sewerage')),)
    resource   = models.IntegerField(_('resource type'), choices = res)
    attrib     = models.IntegerField(_('attributes'), blank = True) # 0 - нет градации, 1 - есть градация
    month      = models.IntegerField(_('month')) # 1 - январь
    year       = models.IntegerField(_('year')) # 2015
    period     = models.IntegerField(_('reporting period')) # 201504 - апрель 2015 г
    tarif      = models.DecimalField(_('tariff 1'), blank = False, max_digits = 15, decimal_places = 5)
    border     = models.DecimalField(_('border 1'), null = True,  blank = True, max_digits = 15, decimal_places = 4)
    tarif2     = models.DecimalField(_('tariff 2'), null = True,  blank = True, max_digits = 15, decimal_places = 5, default = 0)
    border2    = models.DecimalField(_('border 2'), null = True,  blank = True, max_digits = 15, decimal_places = 4, default = 0)
    tarif3     = models.DecimalField(_('tariff 3'), null = True,  blank = True, max_digits = 15, decimal_places = 5, default = 0)
    text       = models.TextField(_('information'), blank=True, default = "")

    class Meta:
        verbose_name = _('tariff')
        verbose_name_plural = _('tariffs')

    def s_res(self):
        if (self.resource == 1):
            return _('electro')
        else:
            if (self.resource == 2):
                return _('gas')
            else:
                if (self.resource == 3):
                    return _('water')
                else:
                    if (self.resource == 4):
                        return _('water supply')
                    else:
                        if (self.resource == 5):
                            return _('sewerage')
                        else:
                            return '???'
  
    def unit(self):
        return a_unit[self.resource]
  
    def s_tarif(self):
        b1 = self.border
        if (b1 == None):
            b1 = 0
        t1 = self.tarif
        if (t1 == None):
            t1 = 0
        b2 = self.border2
        if (b2 == None):
            b2 = 0
        t2 = self.tarif2
        if (t2 == None):
            t2 = 0
        t3 = self.tarif3
        if (t3 == None):
            t3 = 0
        tar = ''
        if (b1 == 0):
            tar = str(t1)
        else:
            tar = str(t1) + ' ' + gettext('until') + ' ' + str(b1) + ' / '
      
        if (b2 == 0):
            tar += str(t2)
        else:
            tar += str(t2) + ' ' + gettext('until') + ' ' + str(b2) + ' / ' + str(t3)
        return tar
          
    def __str__(self):
        return self.s_res() + ': ' + str(self.tarif) + ' ' + gettext('rub.')
  

def get_per_tarif(_user_id, _res, _year, _month):
    ret = {'t1': 0,
           'b1': 0,
           't2': 0,
           'b2': 0,
           't3': 0}

    tarifs = Tarif.objects.filter(user = _user_id, 
                                  resource = _res, 
                                  period__lte = (_year * 100 + _month)).order_by('-period')[:1]
    if (len(tarifs) > 0):
      
        if (tarifs[0].tarif != None):
            ret['t1'] = tarifs[0].tarif;
        else:
            ret['t1'] = 0;
      
        if (tarifs[0].border != None):
            ret['b1'] = tarifs[0].border;
        else:
            ret['b1'] = 0;
      
        if (tarifs[0].tarif2 != None):
            ret['t2'] = tarifs[0].tarif2;
        else:
            ret['t2'] = 0;
      
        if (tarifs[0].border2 != None):
            ret['b2'] = tarifs[0].border2;
        else:
            ret['b2'] = 0;
      
        if (tarifs[0].tarif3 != None):
            ret['t3'] = tarifs[0].tarif3;
        else:
            ret['t3'] = 0;
  
    return ret


class Communal(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    month      = models.IntegerField(_('month')) # 1 - январь
    year       = models.IntegerField(_('year')) # 2015
    period     = models.IntegerField(_('reporting period')) # 201504 - апрель 2015 г
    state      = models.IntegerField(_('state'), blank = True)
                                       # 3 - нет показаний счетчиков и оплаты
                                       # 1 - сняты показания счетчиков, нет оплаты
                                       # 2 - оплачено частично
                                       # 0 - оплачено полностью
    dCounter   = models.DateTimeField(_('meter reading date'), blank = True)
    dPay       = models.DateTimeField(_('pay date'), blank = True)
    # Электроэнергия
    el_old     = models.IntegerField('electro - meter reading old', blank = True)
    el_new     = models.IntegerField('electro - meter reading new', blank = True)
    el_pay     = models.DecimalField('electro - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    # Антенна
    tv_tar     = models.DecimalField('goratorg - accrued', null = True, blank = True, max_digits = 15, decimal_places = 2)
    tv_pay     = models.DecimalField('goratorg - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    # Телефон
    phone_tar  = models.DecimalField('phone - accrued', null = True, blank = True, max_digits = 15, decimal_places = 2)
    phone_pay  = models.DecimalField('phone - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    # Жировка
    zhirovka   = models.DecimalField('account amount', null = True, blank = True, max_digits = 15, decimal_places = 2)
    hot_pay    = models.DecimalField('heatenergy - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    repair_pay = models.DecimalField('overhaul - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    ZKX_pay    = models.DecimalField('HCS - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    # Вода
    cold_old   = models.IntegerField('cold water - meter reading old', blank = True)
    cold_new   = models.IntegerField('cold water - meter reading new', blank = True)
    hot_old    = models.IntegerField('hot water - meter reading old', blank = True)
    hot_new    = models.IntegerField('hot water - meter reading new', blank = True)
    water_pay  = models.DecimalField('water - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
    # Газ
    gas_old    = models.IntegerField('gas - meter reading old', blank = True)
    gas_new    = models.IntegerField('gas - meter reading new', blank = True)
    gas_pay    = models.DecimalField('gas - payment', null = True, blank = True, max_digits = 15, decimal_places = 2)
  
    penalty    = models.DecimalField(_('fine'), null = True, blank = True, max_digits = 15, decimal_places = 2)
    prev_per   = models.DecimalField('previous period', null = True, blank = True, max_digits = 15, decimal_places = 2)
    course     = models.DecimalField('rate', null = True, blank = True, max_digits = 15, decimal_places = 4)
    text       = models.CharField(_('information'), max_length = 1000, blank = True)

    class Meta:
        verbose_name = _('communal payments')
        verbose_name_plural = _('communal payments')

    def __str__(self):
        return str(self.year) + '.' + str(self.month) + ': ' + str(self.zhirovka) + ' ' + gettext('rub.')
  
    def total_usd(self):
        if (self.course == 0):
            return 0
        else:
            return int(self.total_bill() / round(self.course, 0))
  
    def total_pay(self):
        pay = self.tv_pay + self.phone_pay + \
              self.hot_pay + self.repair_pay + self.ZKX_pay + \
              self.el_pay + self.water_pay + self.gas_pay
        return round(pay, 2)
  
    def el_vol(self):
        if (self.el_new == None) or (self.el_old == None):
            return 0
        else:
            return self.el_new - self.el_old
  
    def gs_vol(self):
        if (self.gas_new == None) or (self.gas_old == None):
            return 0
        else:
            return self.gas_new - self.gas_old
  
    def wt_vol(self):
        if (self.cold_new == None) or (self.cold_old == None) or (self.hot_new == None) or (self.hot_old == None):
            return 0
        else:
            return (self.cold_new - self.cold_old) + (self.hot_new - self.hot_old)
  
    def get_tarifs(self, _res):
        return get_per_tarif(self.user.id, _res, self.year, self.month)
  
    def count_by_tarif(self, _res):
  
        if (_res == 1):
            vol = self.el_vol();
        elif (_res == 2):
            vol = self.gs_vol();
        elif (_res == 3) or (_res == 4) or (_res == 5):
            vol = self.wt_vol();
        else:
            vol = 0;
  
        tar = self.get_tarifs(_res)
  
        if (tar['b1'] == 0) or (vol <= tar['b1']):
            return vol * tar['t1']
        else:
            i_sum = tar['b1'] * tar['t1'];
            if (tar['b2'] == 0) or (vol <= tar['b2']):
                return i_sum + (vol - tar['b1']) * tar['t2']
            else:
                return i_sum + (tar['b2'] - tar['b1']) * tar['t2'] + (vol - tar['b2']) * tar['t3']
  
  
    def total_bill(self):
        bill = self.count_by_tarif(1) + self.count_by_tarif(2) + self.count_by_tarif(3) + self.count_by_tarif(4) + self.count_by_tarif(5) + self.tv_tar + self.phone_tar + self.zhirovka
        return round(bill, 2)
  
    def debt(self):
        return round(self.total_bill() - self.total_pay(), 2)
  
    def state_str(self):
        if (self.state == 0):
            return 'Ок'
        elif (self.state == 1):
            return _('meters read but no payment')
        elif (self.state == 2):
            return _('partially paid')
        elif (self.state == 3):
            return _('counters not recorded')
        else:
            return _('unknown status code') + ': ' + str(self.state)
  


def days(_kol):
    if (_kol == 1):
        return '<span style="color:red">' + _('today is the last day') + '.</span>'
    elif (_kol > 1) and (_kol < 5):
        return 'Осталось <span style="color:red">' + str(_kol) + '</span> дня.'
    else:
        return 'Осталось <span style="color:yellow">' + str(_kol) + '</span> дней.'


def subMonths(_y2, _m2, _y1, _m1):
    return (_y2 - _y1 - 1) * 12 + _m2 + (12 - _m1)


def checkPay(_mode, _year, _month):
  now = datetime.now()
  delta = subMonths(now.year, now.month, _year, _month)

  if (delta == 1) and (now.day >= 10) and (now.day <= 25):
    return days(26 - now.day)
  elif (delta < 1) or ((delta == 1) and (now.day < 10)):
    return ''
  else:
    return '<span style="color:red">' + _('payment is past due') + '</span>'


def apart_summary(_user):
  _last = Communal.objects.filter(user = _user).order_by('-period')
  if (len(_last) == 0):
    return _('The amount of rent for the last month, warning about the due date')

  last = _last[0]
  # Определяем за какой месяц была последняя оплата
  if (last.tv_pay  != 0) and (last.phone_pay != 0) and (last.hot_pay   != 0) and (last.repair_pay != 0) and \
     (last.ZKX_pay != 0) and (last.el_pay    != 0) and (last.water_pay != 0) and (last.gas_pay    != 0):
    # Последняя запись - всё оплачено
    if (last.month == 12):
      t_year  = last.year + 1
      t_month = 1
    else:
      t_year  = last.year
      t_month = last.month + 1
    return checkPay(1, t_year, t_month)
  elif (last.tv_pay  != 0) or (last.phone_pay != 0) or (last.hot_pay   != 0) or (last.repair_pay != 0) and \
       (last.ZKX_pay != 0) or (last.el_pay    != 0) or (last.water_pay != 0) or (last.gas_pay    != 0):
    # Последняя запись - оплачено частично
    return checkPay(2, last.year, last.month)
  else:
    # Последняя запись - ничего не оплачено. Считаем, что предыдущий месяц оплачен польностью
    return checkPay(1, last.year, last.month)

    