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
    tot_byn = models.BooleanField(_('totals in BYN'), default = False)
    tot_usd = models.BooleanField(_('totals in USD'), default = False)
    tot_eur = models.BooleanField(_('totals in EUR'), default = False)

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

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.date.strftime('%d.%m.%Y') + ' ' + self.direct.name + ' ' + self.s_summa()

    def name(self):
        res = self.date.strftime('%d.%m.%Y')
        if self.description:
            res += ' - ' + self.description
        return res

    def get_summa(self, currency):
        byn = 0
        if self.price:
            byn = self.price
            if self.qty:
                byn = self.price * self.qty

        if (currency == 'USD'):
            if not self.direct.tot_usd:
                return 0
            if self.usd:
                return self.usd

            if byn and self.rate:
                return byn / self.rate

        if (currency == 'EUR'):
            if not self.direct.tot_eur:
                return 0
            if self.eur:
                return self.eur

            if byn and self.rate_2:
                return byn / self.rate_2

        if (currency == 'BYN'):
            if self.price:
                return byn

            if self.direct.tot_usd and self.usd and self.rate:
                return self.usd * self.rate

            if self.direct.tot_eur and self.eur and self.rate_2:
                return self.eur * self.rate_2

        return 0


    def s_summa(self):
        in_byn, in_usd, in_eur = what_totals(self.direct.id)
    
        res = ''
        if self.direct.tot_usd:
            res = '{:.2F} USD'.format(self.get_summa('USD'))
                                                   
        if self.direct.tot_eur:
            if res:
                res += ', '
            res += '{:.2F} EUR'.format(self.get_summa('EUR'))
        
        if self.direct.tot_byn:
            if res:
                res += ', '
            res += '{:.2F} BYN'.format(self.get_summa('BYN'))
        
        return res
    
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

def what_totals(direct_id):
    if not Projects.objects.filter(id = direct_id).exists():
        return False, False, False
    direct = Projects.objects.filter(id = direct_id).get()
    if (not direct.tot_byn) and (not direct.tot_usd) and (not direct.tot_eur):
        return True, False, False
    else:
        return direct.tot_byn, direct.tot_usd, direct.tot_eur

def get_totals(direct_id):
    byn = 0
    usd = 0
    eur = 0
    in_byn, in_usd, in_eur = what_totals(direct_id)
    for exp in Expenses.objects.filter(direct = direct_id):
        if in_byn:
            byn += exp.get_summa('BYN')
        if in_usd:
            usd += exp.get_summa('USD')
        if in_eur:
            eur += exp.get_summa('EUR')
    return byn, usd, eur
  
def s_proj_summary(direct_id):
    in_byn, in_usd, in_eur = what_totals(direct_id)
    byn, usd, eur = get_totals(direct_id)

    res = ''
    if in_usd:
        res = '{:.2F} USD'.format(usd)
    
    if in_eur:
        if res:
            res += ', '
        res += '{:.2F} EUR'.format(eur)
    
    if in_byn:
        if res:
            res += ', '
        res += '{:.2F} BYN'.format(byn)
    
    return res

