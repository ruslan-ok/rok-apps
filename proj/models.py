from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

app_name = 'proj'

class Projects(models.Model):
    user   = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name   = models.CharField(_('direction'), max_length = 200, blank = False)
    active = models.BooleanField(_('active'), default = False)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)

    class Meta:
        verbose_name = _('direction')
        verbose_name_plural = _('directions')

    def __str__(self):
        return self.name

    def marked_item(self):
        return self.active

    def get_info(self):
        ret = []
        ret.append({'text': s_proj_summary(self.id) })
        return ret

def deactivate_all(user_id, dirs_id):
    for dir in Projects.objects.filter(user = user_id, active = True).exclude(id = dirs_id):
        dir.active = False
        dir.save()

def set_active(user_id, dirs_id):
    if Projects.objects.filter(user = user_id, id = dirs_id).exists():
        dir = Projects.objects.filter(user = user_id, id = dirs_id).get()
        deactivate_all(user_id, dir.id)
        dir.active = True
        dir.save()


class Expenses(models.Model):
    direct = models.ForeignKey(Projects, on_delete = models.CASCADE, verbose_name = _('direct'))
    date = models.DateTimeField(_('date'), default = datetime.now)
    qty = models.DecimalField(_('quantity'), blank = True, null = True, max_digits = 15, decimal_places = 3)
    price = models.DecimalField(_('national currency price'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    rate = models.DecimalField(_('exchange rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    usd = models.DecimalField(_('summa in USD'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    kontr = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    text = models.TextField(_('information'), blank = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.date.strftime('%d.%m.%Y') + ' ' + self.direct.name + ' ' + self.s_summa()

    def name(self):
        return self.date.strftime('%d.%m.%Y')

    def summa(self):
        nc_summa = 0
        usd_summa = 0

        if self.price:
            nc_summa = self.price
            if self.qty:
                nc_summa = self.price * self.qty

        if self.usd:
            usd_summa = self.usd
        elif nc_summa and self.rate:
            usd_summa = nc_summa / self.rate

        return nc_summa, usd_summa

    def s_summa(self):
        nc_summa, usd_summa = self.summa()
        if (usd_summa != 0):
            return '{:.2F} USD'.format(usd_summa)
        return '{:.2F} BYN'.format(nc_summa)
    
    def get_info(self):
        ret = []

        ret.append({'text': '{}: {}'.format(_('summa').capitalize(), self.s_summa()) })

        if self.kontr:
            ret.append({'icon': 'separator'})
            ret.append({'text': self.kontr })
    
        if self.text:
            ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
            ret.append({'text': self.text })
    
        return ret

def proj_summary(direct_id):
    nc_total = 0
    usd_total = 0
    in_usd = True
    if not Projects.objects.filter(id = direct_id).exists():
        return 0, False
    direct = Projects.objects.filter(id = direct_id).get()
    expenses = Expenses.objects.filter(direct = direct.id)
    for exp in expenses:
        nc_summa, usd_summa = exp.summa()
        nc_total += nc_summa
        usd_total += usd_summa
        if in_usd and not usd_summa:
            in_usd = False
    if in_usd:
        return usd_total, True
    else:
        return nc_total, False
  
def s_proj_summary(direct_id):
    total, in_usd = proj_summary(direct_id)
    if not total:
        return '-'
    if in_usd:
        return '{:.2F} USD'.format(total)
    return '{:.2F} BYN'.format(total)

