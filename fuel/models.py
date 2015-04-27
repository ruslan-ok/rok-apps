# coding=UTF-8
from django.contrib.auth.models import User
from django.db import models
from datetime import date
from proj.models import Direct, Proj


class Car(models.Model):
  user   = models.ForeignKey(User)
  name   = models.CharField(u'Модель', max_length = 200, blank = False)
  plate  = models.CharField(u'Гос. номер', max_length = 100)
  active = models.IntegerField(u'Активная', default = 0)
  direct = models.ForeignKey(Direct, null = True)
  def __str__(self):
    return unicode(self.name) + u' [' + unicode(self.plate) + u']'


class Fuel(models.Model):
  car      = models.ForeignKey(Car)
  pub_date = models.DateTimeField(u'Дата заправки')
  odometr  = models.IntegerField(u'Показания одометра', blank=False)
  volume   = models.DecimalField(u'Объём', blank=False, max_digits=5, decimal_places=3)
  price    = models.DecimalField(u'Цена', blank=False, max_digits=15, decimal_places=0)
  comment  = models.CharField(u'Комментарий', max_length=1000, blank=True)
  def __str__(self):
    return unicode(self.pub_date) + u' / ' + unicode(self.odometr) + u' км. / ' + unicode(self.volume) + u' л.'
  def summ(self):
    return int(self.volume * self.price)
  def s_pub_date(self):
    d = str(self.pub_date.day)
    m = str(self.pub_date.month)
    y = str(self.pub_date.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    return d + '.' + m + '.' + y


def fuel_summary(_user):
  try:
    car = Car.objects.get(user = _user, active = 1)
    car_name = car.name + u': '
    fuels = Fuel.objects.filter(car = car.id).order_by('-pub_date', '-odometr')
    counter_max = 0
    counter_min = 0
    total_volume = 0
    
    for f in fuels:
      counter_min = f.odometr
    
      if (counter_max == 0):
        counter_max = f.odometr
      else:
        total_volume += f.volume
    
    km = counter_max - counter_min
    
    if (total_volume == 0) or (km == 0):
      return car_name + u'Не удалось вычислить средний расход'
    
    return car_name + u'<span style="color:yellow">' + str(round((total_volume / km) * 100, 2)) + u'</span> л на 100 км'
  except Car.DoesNotExist:
    return ''
    

class Part(models.Model): # Список расходников
  car      = models.ForeignKey(Car)
  name     = models.CharField(u'Наименование', max_length = 1000, blank = False)
  chg_km   = models.IntegerField(u'Интервал замены, км', blank = True)
  chg_mo   = models.IntegerField(u'Интервал замены, месяцев', blank = True)
  comment  = models.TextField(u'Комментарий', blank = True)
  
  def __str__(self):
    return unicode(self.name)
  
  def last_date(self):
    last = Repl.objects.filter(part = self.id).order_by('-dt_chg')[:1]
    if (len(last) == 0):
      return date.min
    else:
      return last[0].dt_chg.date()

  def s_last_date(self):
    return self.last_date().isoformat()

  def last_odo(self):
    last = Repl.objects.filter(part = self.id).order_by('-dt_chg')[:1]
    if (len(last) == 0):
      return 0
    else:
      return last[0].odometr
  
  def repls(self):
    r = Repl.objects.filter(part = self.id)
    return len(r);


class Repl(models.Model): # Замена расходников
  part     = models.ForeignKey(Part)
  dt_chg   = models.DateTimeField(u'Дата замены', blank = False)
  odometr  = models.IntegerField(u'Показания одометра, км', blank = False)
  manuf    = models.CharField(u'Производитель', max_length = 1000, blank = True)
  part_num = models.CharField(u'Номер по каталогу', max_length = 100, blank = True)
  name     = models.CharField(u'Наименование', max_length = 1000, blank = True)
  oper     = models.ForeignKey(Proj, null = True)
  comment  = models.TextField(u'Комментарий', blank = True, default = None)
  def __str__(self):
    return unicode(self.dt_chg) + u' / ' + unicode(self.odometr) + u' км. / ' + unicode(self.name)
  def s_dt_chg(self):
    d = str(self.dt_chg.day)
    m = str(self.dt_chg.month)
    y = str(self.dt_chg.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    return d + '.' + m + '.' + y

