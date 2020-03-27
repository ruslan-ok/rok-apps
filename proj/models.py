from django.contrib.auth.models import User
from django.db import models

class Direct(models.Model):
  user   = models.ForeignKey(User, on_delete=models.CASCADE)
  name   = models.CharField('Направление', max_length=200, blank=False)
  active = models.IntegerField('Активное', default=0)
  def __str__(self):
    return self.name


class Proj(models.Model):
  direct = models.ForeignKey(Direct, on_delete=models.CASCADE)
  date   = models.DateTimeField('Дата операции')
  kol    = models.DecimalField(blank=False, max_digits=15, decimal_places=3)
  price  = models.DecimalField(blank=False, max_digits=15, decimal_places=2)
  course = models.DecimalField(blank=False, max_digits=15, decimal_places=4)
  usd    = models.DecimalField(blank=False, max_digits=15, decimal_places=2)
  kontr  = models.CharField(max_length=1000, blank=True)
  text   = models.TextField(blank=True)

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
  
