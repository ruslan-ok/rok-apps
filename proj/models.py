from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

app_name = 'proj'

class Direct(models.Model):
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

    def get_info(self):
        return str(self.id)

def deactivate_all(user_id, dirs_id):
    for dir in Direct.objects.filter(user = user_id, active = True).exclude(id = dirs_id):
        dir.active = False
        dir.save()

def set_active(user_id, dirs_id):
    if Direct.objects.filter(user = user_id, id = dirs_id).exists():
        dir = Direct.objects.filter(user = user_id, id = dirs_id).get()
        deactivate_all(user_id, dir.id)
        dir.active = True
        dir.save()


class Proj(models.Model):
    direct = models.ForeignKey(Direct, on_delete = models.CASCADE, verbose_name = _('direct'))
    date   = models.DateTimeField(_('date'), default = datetime.now)
    kol    = models.DecimalField(_('quantity'), blank = False, max_digits = 15, decimal_places = 3)
    price  = models.DecimalField(_('price'), blank = False, max_digits = 15, decimal_places = 2)
    course = models.DecimalField(_('rate'), blank = False, max_digits = 15, decimal_places = 4)
    usd    = models.DecimalField(_('in USD'), blank = False, max_digits = 15, decimal_places = 2)
    kontr  = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    text   = models.TextField(_('information'), blank = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)

    def __str__(self):
        return self.s_date() + ' ' + self.direct.name + ' ' + str(self.summa()) #+ ' ' + self.kontr_cut() + ' ' + self.text_cut()

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def s_date(self):
        d = str(self.date.day)
        m = str(self.date.month)
        y = str(self.date.year)
        if (len(d) < 2):
            d = '0' + d
        if (len(m) < 2):
            m = '0' + m
        return d + '.' + m + '.' + y
    
    def kontr_cut(self):
        if (len(self.kontr) < 11):
            return self.kontr
        return self.kontr[:10] + '...'

    def text_cut(self):
        if (len(self.text) < 21):
            return self.text
        return self.text[:20] + '...'
    
    def summa(self):
        if (self.course == 0):
            return round(self.usd, 2)
        else:
            return round(self.usd + ((self.kol * self.price) / self.course), 2)

    def get_info(self):
        ret = []

        ret.append({'text': '{}: {}'.format(_('summa').capitalize(), self.summa()) })

        if self.kontr:
            ret.append({'icon': 'separator'})
            ret.append({'text': self.kontr })
    
        if self.text:
            ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
    
        return ret

def proj_summary(_user):
    try:
        cur_dir = Direct.objects.get(user = _user, active = 1)
        opers = Proj.objects.filter(direct = cur_dir.id)
        tot = 0
        for o in opers:
            tot += o.summa()
        return cur_dir.name + ': <span id="warning">' + str(int(tot)) + '</span>$'
    except Direct.DoesNotExist:
        return ''
  
