from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Car(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('model'), max_length = 200, blank = False)
    plate  = models.CharField(_('car number'), max_length = 100)
    active = models.BooleanField(_('active'), default = False)

class Fuel(models.Model):
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    pub_date = models.DateTimeField(_('date'), default = datetime.now)
    odometr  = models.IntegerField(_('odometer'), blank=False)
    volume   = models.DecimalField(_('volume'), blank=False, max_digits=5, decimal_places=3)
    price    = models.DecimalField(_('price'), blank=False, max_digits=15, decimal_places=2)
    comment  = models.CharField(_('information'), max_length=1000, blank=True)
    created  = models.DateTimeField(_('creation time'), auto_now_add = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)

class Part(models.Model): # Consumable
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    name     = models.CharField(_('name'), max_length = 1000, blank = False)
    chg_km   = models.IntegerField(_('replacement interval, km'), blank = True, null = True)
    chg_mo   = models.IntegerField(_('replacement interval, months'), blank = True, null = True)
    comment  = models.TextField(_('information'), blank = True)

class Repl(models.Model): # Replacement of consumables
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'), null = True)
    part     = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name=_('part'), null = True)
    dt_chg   = models.DateTimeField(_('date'), blank = False)
    odometr  = models.IntegerField(_('odometer, km'), blank = False)
    manuf    = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    part_num = models.CharField(_('catalog number'), max_length = 100, blank = True)
    descr    = models.CharField(_('name'), max_length = 1000, blank = True)
    comment  = models.TextField(_('information'), blank = True, default = None, null = True)
    created  = models.DateTimeField(_('creation time'), auto_now_add = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)
