from django.contrib.auth.models import User
from django.db import models
from datetime import date
from proj.models import Direct, Proj
from django.utils.translation import gettext, gettext_lazy as _


class Car(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('model'), max_length = 200, blank = False)
    plate  = models.CharField(_('car number'), max_length = 100)
    active = models.BooleanField(_('active'), default = False)

    class Meta:
        verbose_name = _('car')
        verbose_name_plural = _('cars')

    def __str__(self):
        return self.name + ' [' + self.plate + ']'

    def s_active(self):
        if self.active:
            return '*'
        else:
            return ''

def deactivate_all(user_id, cars_id):
    for car in Car.objects.filter(user = user_id, active = True).exclude(id = cars_id):
        car.active = False
        car.save()

def set_active(user_id, cars_id):
    if Car.objects.filter(user = user_id, id = cars_id).exists():
        car = Car.objects.filter(user = user_id, id = cars_id).get()
        deactivate_all(user_id, car.id)
        car.active = True
        car.save()


class Fuel(models.Model):
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    pub_date = models.DateTimeField(_('date'))
    odometr  = models.IntegerField(_('odometer'), blank=False)
    volume   = models.DecimalField(_('volume'), blank=False, max_digits=5, decimal_places=3)
    price    = models.DecimalField(_('price'), blank=False, max_digits=15, decimal_places=2)
    comment  = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('fueling')
        verbose_name_plural = _('fuelings')

    def __str__(self):
        return str(self.pub_date) + ' / ' + str(self.odometr) + ' ' + gettext('km.') +' / ' + str(self.volume) + ' ' + gettext('l.')
    
    def summa(self):
        return self.price * self.volume

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
    car = Car.objects.get(user = _user, active = True)
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
    car = Car.objects.get(user = _user, active = True)
    car_name = car.name + ': '
    cons = consumption(_user)
    if (cons == 0):
      return car_name + gettext('failed to calculate average consumption')
    else:
      return car_name + '<span class="warning">' + str(cons) + '</span> ' + gettext(' l. per 100 km')
  except Car.DoesNotExist:
    return gettext('no active car')
    

class Part(models.Model): # Список расходников
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    name     = models.CharField(_('name'), max_length = 1000, blank = False)
    chg_km   = models.IntegerField(_('replacement interval, km'), blank = True)
    chg_mo   = models.IntegerField(_('replacement interval, months'), blank = True)
    comment  = models.TextField(_('information'), blank = True)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')
  
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
        return len(r)

    def chg_km_th(self):
        return self.chg_km // 1000

    def get_rest(self):
        if ((not self.chg_km) and (not self.chg_mo)) or (not self.last_odo()):
            return ''

        fuels = Fuel.objects.filter(car = self.car).order_by('-pub_date')[:1]
        if (len(fuels) == 0):
            return ''

        output = ''
        p1 = ''
        p2 = ''
        m1 = False
        m2 = False

        if (self.chg_km != 0):
            trip_km_unround = fuels[0].odometr - self.last_odo() # Проехали км от последней замены
          
            trip_km = trip_km_unround
            if (trip_km > 1000):
                trip_km = round(trip_km_unround / 1000) * 1000
          
            if (trip_km_unround > self.chg_km):
                if ((trip_km_unround - self.chg_km) > 1000):
                    p1 = '<span class="error">просрочено на ' + str(round(((trip_km_unround - self.chg_km) / 1000))) + ' тыс. км</span>'
                else:
                    p1 = '<span class="error">просрочено на ' + str(trip_km_unround - self.chg_km) + ' км</span>'
                m1 = True
            else:
                if ((self.chg_km - trip_km) < 1000):
                    p1 = '<span class="warning">' + str(self.chg_km - trip_km_unround) + ' км</span>'
                else:
                    p1 = str(round(((self.chg_km - trip_km) / 1000))) + ' тыс. км'
              
        if (self.chg_mo != 0):
            trip_days = (fuels[0].pub_date.date() - self.last_date()).days - self.chg_mo * 30.42
            per = ''
            days = trip_days
            if (days < 0):
                days = -1 * days
          
            if (days < 2):
                per = 'день'
            elif (days < 5):
                per = str(round(days)) + ' дня'
            elif (days < 30):
                per = str(round(days)) + ' дней'
            elif (days < 45):
                per = 'месяц'
            elif (days < 135):
                per = str(round(days/30)) + ' месяца'
            elif (days < 270):
                per = 'пол года'
            elif (days < 540):
                per = 'год'
            elif (days < 1642):
                per = str(round(days/365)) + ' года'
            else:
                per = str(round(days/365)) + ' лет'
            
            if (trip_days > 0):
                p2 = '<span class="error">просрочено на ' + per + '</span>'
                m2 = True
            else:
                if (days < 32):
                    p2 = '<span class="warning">' + per + '</span>'
                else:
                    p2 = per
      
        if m1:
            output = p1
        elif m2:
            output = p2
        elif (p1 == ''):
            output = p2
        elif (p2 == ''):
            output = p1
        else:
            output = p1 + ' или ' + p2

        return output


class Repl(models.Model): # Замена расходников
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'), null = True)
    part     = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name=_('part'))
    dt_chg   = models.DateTimeField(_('date'), blank = False)
    odometr  = models.IntegerField(_('odometer, km'), blank = False)
    manuf    = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    part_num = models.CharField(_('catalog number'), max_length = 100, blank = True)
    name     = models.CharField(_('name'), max_length = 1000, blank = True)
    # deprecated
    oper     = models.ForeignKey(Proj, on_delete=models.CASCADE, null = True, verbose_name=_('project'))
    comment  = models.TextField(_('information'), blank = True, default = None)

    class Meta:
        verbose_name = _('replacement')
        verbose_name_plural = _('replacements')

    def __str__(self):
        return str(self.dt_chg) + ' / ' + str(self.odometr) + ' ' + gettext('km.') + ' / ' + self.name

    def s_dt_chg(self):
        d = str(self.dt_chg.day)
        m = str(self.dt_chg.month)
        y = str(self.dt_chg.year)
        if (len(d) < 2):
            d = '0' + d
        if (len(m) < 2):
            m = '0' + m
        return d + '.' + m + '.' + y

def init_repl_car():
    for repl in Repl.objects.filter(car__isnull = True):
        repl.car = repl.part.car
        repl.save()
        