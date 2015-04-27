# coding=UTF-8
from django.contrib.auth.models import User
from django.db import models


class Person(models.Model):
  user   = models.ForeignKey(User)
  name   = models.CharField(max_length=500, blank=False)
  dative = models.CharField(max_length=500, blank=False)
  me     = models.IntegerField()
  def __str__(self):
    return '[' + str(self.user) + '] ' + self.name

class Saldo(models.Model):
  user   = models.ForeignKey(User)
  p1   = models.ForeignKey(Person, related_name="p1")
  p2   = models.ForeignKey(Person, related_name="p2")
  me   = models.IntegerField(blank=False)
  summ = models.IntegerField(blank=False)

class Trip(models.Model):
  user      = models.ForeignKey(User)
  year      = models.IntegerField(blank=False)
  week      = models.IntegerField(blank=False)
  days      = models.IntegerField(blank=False)
  oper      = models.IntegerField(blank=False)
  price     = models.IntegerField(blank=False)
  driver    = models.ForeignKey(Person, related_name="driver")
  passenger = models.ForeignKey(Person, related_name="passenger")
  text      = models.CharField(max_length=1000, blank=True)

  def s_days(self):
    if (self.oper != 0):
      return ''

    s = '';
    for i in range(0, 7):
      n = 0
      m = 0
      for j in range(0, 2):
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
      return 'проезд'
    else:
      return 'оплата'

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
      return self.price

    kol = 0
    for i in range(0, 7):
      for j in range(0, 2):
        if (int(self.days) & (1 << (i*2+j))):
          kol = kol + 1
    return kol * self.price


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


def trip_summary(_user):
  ret = u''
  saldos = Saldo.objects.filter(user = _user)
  
  for s in saldos:
    if (s.summ != 0):
      if (ret != u''):
        ret += u', '
      if (s.summ < 0):
        ret += NameI(s.p1) + ' ' + NameD(s.p2) + ' ' + str(-1*s.summ)
      else:
        ret += NameI(s.p2) + ' ' + NameD(s.p1) + ' ' + str(s.summ)
  
  return u'<span style="color:yellow">' + ret + u'</span>'
