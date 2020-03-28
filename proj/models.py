from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

class Direct(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('direction'), max_length=200, blank=False)
    active = models.IntegerField(_('active'), default=0)

    class Meta:
        verbose_name = _('direct')
        verbose_name_plural = _('directs')

    def __str__(self):
        return self.name


class Proj(models.Model):
    direct = models.ForeignKey(Direct, on_delete=models.CASCADE, verbose_name=_('direct'))
    date   = models.DateTimeField(_('date'))
    kol    = models.DecimalField(_('quantity'), blank=False, max_digits=15, decimal_places=3)
    price  = models.DecimalField(_('price'), blank=False, max_digits=15, decimal_places=2)
    course = models.DecimalField(_('rate'), blank=False, max_digits=15, decimal_places=4)
    usd    = models.DecimalField(_('in USD'), blank=False, max_digits=15, decimal_places=2)
    kontr  = models.CharField(_('manufacturer'), max_length=1000, blank=True)
    text   = models.TextField(_('information'), blank=True)

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
  
