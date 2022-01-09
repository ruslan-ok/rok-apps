from decimal import *
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _


app_name = 'trip'
PERS = 'persons'
TRIP = 'trips'


class Person(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('name'), max_length=500, blank=False)
    dative = models.CharField(_('dative'), max_length=500, blank=False)
    me     = models.BooleanField(_('me'), default=False)

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.name

    def marked_item(self):
        return self.me

    def get_info(self):
        ret = []
        ret.append({'text': self.dative})
        return ret


def deactivate_all(user_id, person_id):
    for person in Person.objects.filter(user = user_id, me = True).exclude(id = person_id):
        person.me = False
        person.save()

def set_active(user_id, person_id):
    if Person.objects.filter(user = user_id, id = person_id).exists():
        person = Person.objects.filter(user = user_id, id = person_id).get()
        deactivate_all(user_id, person.id)
        person.me = True
        person.save()

class Saldo(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    p1   = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='p1', verbose_name=_('person 1'))
    p2   = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='p2', verbose_name=_('person 2'))
    me   = models.BooleanField(_('me'), blank=False, default=False)
    summ = models.DecimalField(_('summa'), blank=False, max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('saldo')
        verbose_name_plural = _('saldos')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.p1.name + ' ' + self.p2.name + ' ' + str(self.summ)

class Trip(models.Model):
    user      = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    year      = models.IntegerField(_('year'), blank = False)
    week      = models.IntegerField(_('week'), blank = False)
    days      = models.IntegerField(_('days'), blank = False, default = 0)
    oper      = models.IntegerField(_('operation'), blank = False, default = 0)
    price     = models.DecimalField(_('price'), blank = False, max_digits = 15, decimal_places = 2, default = 0)
    driver    = models.ForeignKey(Person, on_delete = models.CASCADE, related_name = 'driver', verbose_name = _('driver'))
    passenger = models.ForeignKey(Person, on_delete = models.CASCADE, related_name = 'passenger', verbose_name = _('passenger'))
    text      = models.CharField(_('information'), max_length = 1000, blank = True)
    modif     = models.DateTimeField(_('last modification'), blank = True, auto_now = True)

    class Meta:
        verbose_name = _('trip')
        verbose_name_plural = _('trips')

    def __str__(self):
        return '[' + self.user.username + '] ' + str(self.year) + ' ' + gettext('week') + ': ' + str(self.week) + ', ' + self.s_oper() + ', ' + \
               gettext('driver') + ': ' + self.s_driv() + ', ' + gettext('passenger') + ': ' + self.s_pass() + ', ' + gettext('summa') + ': ' + str(self.summa())

    def s_days(self):
        if (self.oper != 0):
            return ''

        s = '';
        for i in range(7):
            n = 0
            m = 0
            for j in range(2):
                if (self.days & (1 << (i*2+j))):
                    n = n + 1
                    if (j == 0):
                        m = 1
            if (n == 0):
                s += '-'
            elif (n == 1):
                if (m == 1):
                    s += '\''
                else:
                    s += '.'
            else:
                s += ':'
        return s
    
    def s_oper(self):
        if (self.oper == 0):
            return gettext('driveway')
        else:
            return gettext('payment')
    
    def s_prc(self):
        if (self.oper == 0):
            return self.price
        else:
            return ''
    
    def c_oper(self):
        if (self.oper == 0):
            return 'oper_trip'
        else:
            return 'oper_pay'
    
    def s_driv(self):
        pers = Person.objects.get(id = self.driver.id)
        return pers.name
    
    def s_pass(self):
        pers = Person.objects.get(id = self.passenger.id)
        return pers.name
    
    def summa(self):
        if (self.oper == 1):
            return Decimal(self.price)
    
        kol = 0
        for i in range(0, 7):
            for j in range(0, 2):
                if (int(self.days) & (1 << (i*2+j))):
                    kol = kol + 1
        return Decimal(kol * self.price)

    def name(self):
        return str(self.week) + '-' + str(self.year) + ': ' + gettext('driver') + ': ' + self.s_driv() + ', ' + gettext('passenger') + ': ' + self.s_pass()

    def get_info(self):
        ret = []
        ret.append({'text': gettext('summa') + ': ' + str(self.summa())})
        if (self.oper == 0):
            ret.append({'icon': 'separator'})
            ret.append({'text': ' ' + self.s_days()})
        if self.text:
            ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
        return ret

    def marked_item(self):
        return (self.oper == 0)


def NameI(p):
    try:
        pers = Person.objects.get(id = p.id)
        return pers.name
    except Person.DoesNotExist:
        return '?'


def NameD(p):
    try:
        pers = Person.objects.get(id = p.id)
        return pers.dative
    except Person.DoesNotExist:
        return '?'


def trip_summary(_user, with_span = True):
    ret = ''
    saldos = Saldo.objects.filter(user = _user)
    
    for s in saldos:
        if (s.summ != 0):
            if (ret != ''):
                ret += ', '
            if (s.summ < 0):
                ret += NameI(s.p1) + ' ' + NameD(s.p2) + ' ' + str(-1*s.summ)
            else:
                ret += NameI(s.p2) + ' ' + NameD(s.p1) + ' ' + str(s.summ)
    
    if not with_span:
        return ret

    return '<span id="warning">' + ret + '</span>'


