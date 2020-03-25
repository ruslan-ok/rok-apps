from django.contrib.auth.models import User
from django.db import models
from datetime import date
from proj.models import Direct, Proj


class Car(models.Model):
  user   = models.ForeignKey(User, on_delete=models.CASCADE)
  name   = models.CharField('Модель', max_length = 200, blank = False)
  plate  = models.CharField('Гос. номер', max_length = 100)
  active = models.IntegerField('Активная', default = 0)
  direct = models.ForeignKey(Direct, on_delete=models.CASCADE, null = True)
  def __str__(self):
    return self.name + ' [' + self.plate + ']'


class Fuel(models.Model):
  car      = models.ForeignKey(Car, on_delete=models.CASCADE)
  pub_date = models.DateTimeField('Дата заправки')
  odometr  = models.IntegerField('Показания одометра', blank=False)
  volume   = models.DecimalField('Объём', blank=False, max_digits=5, decimal_places=3)
  price    = models.DecimalField('Цена', blank=False, max_digits=15, decimal_places=2)
  comment  = models.CharField('Комментарий', max_length=1000, blank=True)
  def __str__(self):
    return str(self.pub_date) + ' / ' + str(self.odometr) + ' км. / ' + str(self.volume) + ' л.'
  def summ(self):
    return float(self.price * self.volume)
  def s_pub_date(self):
    d = str(self.pub_date.day)
    m = str(self.pub_date.month)
    y = str(self.pub_date.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    return d + '.' + m + '.' + y


def consumption(_user):
  try:
    car = Car.objects.get(user = _user, active = 1)
    car_name = car.name + ': '
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
      return 0
    
    return round((total_volume / km) * 100, 2)
  except Car.DoesNotExist:
    return 0
    

def fuel_summary(_user):
  try:
    car = Car.objects.get(user = _user, active = 1)
    car_name = car.name + ': '
    cons = consumption(_user)
    if (cons == 0):
      return car_name + 'Не удалось вычислить средний расход'
    else:
      return car_name + '<span id="warning">' + str(cons) + '</span> л на 100 км'
  except Car.DoesNotExist:
    return 'Нет активного автомобиля'
    

class Part(models.Model): # Список расходников
  car      = models.ForeignKey(Car, on_delete=models.CASCADE)
  name     = models.CharField('Наименование', max_length = 1000, blank = False)
  chg_km   = models.IntegerField('Интервал замены, км', blank = True)
  chg_mo   = models.IntegerField('Интервал замены, месяцев', blank = True)
  comment  = models.TextField('Комментарий', blank = True)
  
  def __str__(self):
    return self.name
  
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
  part     = models.ForeignKey(Part, on_delete=models.CASCADE)
  dt_chg   = models.DateTimeField('Дата замены', blank = False)
  odometr  = models.IntegerField('Показания одометра, км', blank = False)
  manuf    = models.CharField('Производитель', max_length = 1000, blank = True)
  part_num = models.CharField('Номер по каталогу', max_length = 100, blank = True)
  name     = models.CharField('Наименование', max_length = 1000, blank = True)
  oper     = models.ForeignKey(Proj, on_delete=models.CASCADE, null = True)
  comment  = models.TextField('Комментарий', blank = True, default = None)
  def __str__(self):
    return str(self.dt_chg) + ' / ' + str(self.odometr) + ' км. / ' + self.name
  def s_dt_chg(self):
    d = str(self.dt_chg.day)
    m = str(self.dt_chg.month)
    y = str(self.dt_chg.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    return d + '.' + m + '.' + y

