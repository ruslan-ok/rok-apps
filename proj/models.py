from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Projects(models.Model):
    user   = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name   = models.CharField(_('direction'), max_length = 200, blank = False)
    active = models.BooleanField(_('active'), default = False)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    tot_byn = models.BooleanField(_('totals in BYN'), default = False)
    tot_usd = models.BooleanField(_('totals in USD'), default = False)
    tot_eur = models.BooleanField(_('totals in EUR'), default = False)

class Expenses(models.Model):
    direct = models.ForeignKey(Projects, on_delete = models.CASCADE, verbose_name = _('direct'))
    date = models.DateTimeField(_('date'), default = datetime.now)
    description = models.CharField(_('name'), max_length = 1000, blank = True)
    qty = models.DecimalField(_('quantity'), blank = True, null = True, max_digits = 15, decimal_places = 3, default = 1)
    price = models.DecimalField(_('national currency price'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    rate = models.DecimalField(_('USD exchange rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    rate_2 = models.DecimalField(_('EUR exchange rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    usd = models.DecimalField(_('summa in USD'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    eur = models.DecimalField(_('summa in EUR'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    kontr = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    text = models.TextField(_('information'), blank = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
