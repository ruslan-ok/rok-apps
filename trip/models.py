from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Person(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('name'), max_length=500, blank=False)
    dative = models.CharField(_('dative'), max_length=500, blank=False)
    me     = models.BooleanField(_('me'), default=False)

class Saldo(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    p1   = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='p1', verbose_name=_('person 1'))
    p2   = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='p2', verbose_name=_('person 2'))
    me   = models.BooleanField(_('me'), blank=False, default=False)
    summ = models.DecimalField(_('summa'), blank=False, max_digits=15, decimal_places=2)

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


