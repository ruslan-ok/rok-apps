from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _

term_names = {0: _('overdue'),
              1: _('today'),
              2: _('tomorow'),
              3: _('this week'),
              4: _('next week'),
              5: _('later'),
              6: _('no deadline')}

group_names = {0: _('sandbox'),
               1: _('work'),
               2: _('auto'),
               3: _('bike'),
               4: _('Sheipichy')}

imptnc_names = {0: _('not matter'),
                1: _('usually'),
                2: _('important'),
                3: _('very important'),
                4: _('critical')}

color_names = {0: _('color1'), 
               1: _('color2'),
               2: _('color3'),
               3: _('color4'),
               4: _('color5')}

compl_names = {0: _('not completed'),
               1: _('completed'),
               2: _('all')}

sort_names = {0: _('term'),
              1: _('name'),
              2: _('code'),
              3: _('importance'),
              4: _('group code'),
              5: _('color')}

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
    user     = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name     = models.CharField(_('name'), max_length = 200, blank = False)
    comment  = models.CharField(_('description'), max_length = 2000, blank = True)
    active   = models.IntegerField(_('active'), default = 0)
    sort     = models.IntegerField(_('sorting'), default = 0)

    class Meta:
        verbose_name = _('task group')
        verbose_name_plural = _('task groups')

    def __str__(self):
        return self.name


class Task(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    pub_date = models.DateTimeField(_('date'), default = timezone.now)
    name     = models.CharField(_('name'), max_length = 200, blank = False)
    code     = models.CharField(_('code'), max_length = 200, blank = True)
    grp      = models.ForeignKey(TGroup, on_delete=models.CASCADE, blank = True, null = True, verbose_name=_('group'))
    d_exec   = models.DateField(_('deadline (date)'), blank = True, null = True)
    t_exec   = models.TimeField(_('deadline (time)'), blank = True, null = True)
    repeat   = models.IntegerField(_('repeat'), default = 0) 
    # 0 - нет, 1 - ежедневно, 2 - еженедельно, 3 - ежемесячно, 4 - ежегодно
    cycle    = models.IntegerField(_('repetition method'), default = 0) 
    # ежедневно:   0 - каждый указанный день, 1 - каждый рабочий день, 2 - через заданное количество дней после завершения
    # еженедельно: 0 - каждую неделю в указанные дни, 1 - через заданное количество недель после завершения
    # ежемесячно:  0 - каждый указанный месяц указанного числа, 1 - в указанный день недели, 2- через заданное количество месяцев после завершения
    # ежегодно:    0 - каждый указанный год, 1 - в указанныйдень недели указанного месяца, 2 - через заданное количество лет после завершения
    step     = models.IntegerField(_('step'), default = 1)
    # через сколько циклов повторять или номер недели (1, 2, 3, 4, последняя)
    value1   = models.IntegerField(_('calendar element 1'), default = 0)
    # еженедельно: выбранные дни недели
    # ежемесячно:  число или номер недели
    # ежегодно:    выбранный месяц
    value2   = models.IntegerField(_('calendar element 2'), default = 0)
    # ежемесячно:  день недели
    # ежегодно:    выбранный день недели
    done     = models.IntegerField(_('executions'), default = 0)
    start    = models.DateTimeField(_('start date'), blank = True, null = True)
    stop_mode= models.IntegerField(_('completion method'), default = 0)
    # 0 - нет конечной даты, 1 - завершить после указанного количества повторений, 2 - дата окончания
    count    = models.IntegerField(_('number of repetitions'), default = 10)
    stop     = models.DateTimeField(_('stop date'), blank = True, null = True)
    comment  = models.CharField(_('description'), max_length = 2000, blank = True)
    active   = models.IntegerField(_('active'), default = 1)
    attrib   = models.IntegerField(_('task attributes'), default = 0, blank = True)
    color    = models.IntegerField(_('color'), default = 0, blank = True, null = True)
    # Пока не используется

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return self.name

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
    return _('total tasks') + ': <span id="warning">' + str(len(tasks)) + '</span>'


class TaskView(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name     = models.CharField(_('name'), max_length = 200, blank = False)
    code     = models.CharField(_('sort number'), max_length = 200, blank = True, default = '')
    active   = models.IntegerField(_('active'), default = 0)
    fltr     = models.IntegerField(_('filter'), default = 0) # Битовая маска для "Группа", "Срок", "Важность", "Цвет"
    sort     = models.IntegerField(_('sorting'), default = 0)
    grp      = models.IntegerField(_('grouping'), default = 0)
    flds     = models.IntegerField(_('fields'), default = 0)

    class Meta:
        verbose_name = _('task view')
        verbose_name_plural = _('task views')

    def __str__(self):
        return self.name

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
    view     = models.ForeignKey(TaskView, on_delete=models.CASCADE, verbose_name=_('view'))
    entity   = models.IntegerField(_('entity'), default = 0)
    npp      = models.IntegerField(_('sort number'), default = 0)
    value    = models.IntegerField(_('value'), default = 0)
    direct   = models.IntegerField(_('sort direction'), default = 0)

    class Meta:
        verbose_name = _('task filter')
        verbose_name_plural = _('task filters')

    def f_name(self):
        return (fltr_names[self.entity])[self.value]
