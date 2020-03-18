# coding=UTF-8
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import date

term_names = {0: 'Просроченные',
              1: 'Сегодня',
              2: 'Завтра',
              3: 'Эта неделя',
              4: 'Следующая неделя',
              5: 'Позже',
              6: 'Срок не задан'}

group_names = {0: 'Песочница',
               1: 'Работа',
               2: 'Авто',
               3: 'Вело',
               4: 'Шейпичи'}

imptnc_names = {0: 'не важно',
                1: 'обычно',
                2: 'важно',
                3: 'очень важно',
                4: 'критично'}

color_names = {0: 'цвет1', 
               1: 'цвет2',
               2: 'цвет3',
               3: 'цвет4',
               4: 'цвет5'}

compl_names = {0: 'не выполнены',
               1: 'выполнены',
               2: 'все'}

sort_names = {0: 'Срок',
              1: 'Наименование',
              2: 'Код',
              3: 'Важность',
              4: 'Код группы',
              5: 'Цвет'}

FLTR_TERM       = 0 #Срок
FLTR_GROUP      = 1 #Группа
FLTR_IMPORTANCE = 2 #Важность
FLTR_COLOR      = 3 #Цвет
FLTR_COMPLETE   = 4 #Исполнение
SORTS           = 5 #Сортировки


fltr_names = {
    FLTR_GROUP: group_names,
    FLTR_TERM: term_names,
    FLTR_IMPORTANCE: imptnc_names,
    FLTR_COLOR: color_names,
    FLTR_COMPLETE: compl_names,
    SORTS: sort_names}

filters = {FLTR_GROUP, FLTR_TERM, FLTR_IMPORTANCE, FLTR_COLOR, FLTR_COMPLETE}


class TGroup(models.Model):
  user     = models.ForeignKey(User)
  name     = models.CharField(u'Наименование', max_length = 200, blank = False)
  comment  = models.CharField(u'Описание', max_length = 2000, blank = True)
  active   = models.IntegerField(u'Активна', default = 0)
  sort     = models.IntegerField(u'Сортировка', default = 0)
  def __str__(self):
    return self.name.encode('utf-8')


class Task(models.Model):
  user     = models.ForeignKey(User)
  pub_date = models.DateTimeField(u'Дата создания', default = timezone.now)
  name     = models.CharField(u'Наименование', max_length = 200, blank = False)
  code     = models.CharField(u'Код', max_length = 200, blank = True)
  grp      = models.ForeignKey(TGroup, blank = True, null = True)
  d_exec   = models.DateField(u'Срок исполнения (дата)', blank = True, null = True)
  t_exec   = models.TimeField(u'Срок исполнения (время)', blank = True, null = True)
  repeat   = models.IntegerField(u'Повторение', default = 0) 
  # 0 - нет, 1 - ежедневно, 2 - еженедельно, 3 - ежемесячно, 4 - ежегодно
  cycle    = models.IntegerField(u'Способ повторения', default = 0) 
  # ежедневно:   0 - каждый указанный день, 1 - каждый рабочий день, 2 - через заданное количество дней после завершения
  # еженедельно: 0 - каждую неделю в указанные дни, 1 - через заданное количество недель после завершения
  # ежемесячно:  0 - каждый указанный месяц указанного числа, 1 - в указанный день недели, 2- через заданное количество месяцев после завершения
  # ежегодно:    0 - каждый указанный год, 1 - в указанныйдень недели указанного месяца, 2 - через заданное количество лет после завершения
  step     = models.IntegerField(u'Шаг', default = 1)
  # через сколько циклов повторять или номер недели (1, 2, 3, 4, последняя)
  value1   = models.IntegerField(u'Элемент календаря 1', default = 0)
  # еженедельно: выбранные дни недели
  # ежемесячно:  число или номер недели
  # ежегодно:    выбранный месяц
  value2   = models.IntegerField(u'Элемент календаря 2', default = 0)
  # ежемесячно:  день недели
  # ежегодно:    выбранный день недели
  done     = models.IntegerField(u'Выполнено раз', default = 0)
  start    = models.DateTimeField(u'Дата начала', blank = True, null = True)
  stop_mode= models.IntegerField(u'Способ завершения', default = 0)
  # 0 - нет конечной даты, 1 - завершить после указанного количества повторений, 2 - дата окончания
  count    = models.IntegerField(u'Количество повторений', default = 10)
  stop     = models.DateTimeField(u'Дата окончания', blank = True, null = True)
  comment  = models.CharField(u'Описание', max_length = 2000, blank = True)
  active   = models.IntegerField(u'Активна', default = 1)
  attrib   = models.IntegerField(u'Атрибуты задачи', default = 0, blank = True)
  color    = models.IntegerField(u'Атрибуты задачи', default = 0, blank = True)
  # Пока не используется
  def __str__(self):
    return self.name.encode('utf-8')
  def s_due(self):
    if (self.d_exec == None):
      return '---'
    d = str(self.d_exec.day)
    m = str(self.d_exec.month)
    y = str(self.d_exec.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    if (self.t_exec == None):
      return d + '.' + m + '.' + y
    h = str(self.t_exec.hour)
    n = str(self.t_exec.minute)
    if (len(h) < 2):
      h = '0' + h
    if (len(n) < 2):
      n = '0' + n
    return d + '.' + m + '.' + y + ' ' + h + ':' + n


def task_summary(_user):
  tasks = Task.objects.filter(user = _user)
  return u'Всего задач: <span id="warning">' + str(len(tasks)) + u'</span>'


class TaskView(models.Model):
  user     = models.ForeignKey(User)
  name     = models.CharField(u'Наименование', max_length = 200, blank = False)
  code     = models.CharField(u'Код для сортировки', max_length = 200, blank = True, default = '')
  active   = models.IntegerField(u'Активна', default = 0)
  fltr     = models.IntegerField(u'Фильтр', default = 0) # Битовая маска для "Группа", "Срок", "Важность", "Цвет"
  sort     = models.IntegerField(u'Сортировка', default = 0)
  grp      = models.IntegerField(u'Группировка', default = 0)
  flds     = models.IntegerField(u'Поля', default = 0)
  def __str__(self):
    return self.name.encode('utf-8')
  def s_fltr(self):
    ret = ''

    for f in filters:
      fe = TaskFilter.objects.filter(view = self.id, entity = f).order_by('npp')
      for fv in fe:
        if (ret != ''):
          ret += ', '
        ret += fv.f_name()
      if (ret != ''):
        ret += '. '

    return ret

  def s_sort(self):
    ret = ''
    sorts = TaskFilter.objects.filter(view = self.id, entity = SORTS).order_by('npp')           #Сортировки
    for ss in sorts:
      if (ret != ''):
        ret += ', '
      ret += ss.f_name()
    return ret
  def s_flds(self):
    return '?'

class TaskFilter(models.Model):
  view     = models.ForeignKey(TaskView)
  entity   = models.IntegerField(u'Сущность', default = 0)
  npp      = models.IntegerField(u'Номер по порядку', default = 0)
  value    = models.IntegerField(u'Значение', default = 0)
  direct   = models.IntegerField(u'Направление сортировки', default = 0)
  def f_name(self):
    return (fltr_names[self.entity])[self.value]
