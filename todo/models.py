from datetime import datetime, date
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .utils import nice_date, GRPS_PLANNED

class Grp(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    node = models.ForeignKey('self', on_delete = models.CASCADE, verbose_name = _('node'), blank = True, null = True)
    name = models.CharField(_('group name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)
    is_open = models.BooleanField(_('node is open'), default = False)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name


class Lst(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    grp = models.ForeignKey(Grp, on_delete = models.CASCADE, verbose_name = _('group'), blank = True, null = True)
    name = models.CharField(_('list name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)

    class Meta:
        verbose_name = _('list')
        verbose_name_plural = _('lists')

    def __str__(self):
        return self.name


NONE = 0
DAILY = 1
WORKDAYS = 2
WEEKLY = 3
MONTHLY = 4
ANNUALLY = 5

REPEAT = [
    (NONE, _('no')),
    (DAILY, _('daily')),
    (WORKDAYS, _('work days')),
    (WEEKLY, _('weekly')),
    (MONTHLY, _('monthly')),
    (ANNUALLY, _('annually')),
]

REPEAT_SELECT = [
    (DAILY, _('days')),
    (WEEKLY, _('weeks')),
    (MONTHLY, _('months')),
    (ANNUALLY, _('years')),
]

REPEAT_NAME = {
    DAILY: _('days'),
    WEEKLY: _('weeks'),
    MONTHLY: _('months'),
    ANNUALLY: _('years'),
}

class Task(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_user')
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    name = models.CharField(_('name'), max_length = 200, blank = False)
    start = models.DateField(_('start date'), blank = True, null = True)
    stop = models.DateField(_('stop date'), blank = True, null = True)
    completed = models.BooleanField(_('completed'), default = False)
    completion = models.DateTimeField(_('completion time'), blank = True, null = True, default = None)
    in_my_day = models.BooleanField(_('in my day'), default = False)
    important = models.BooleanField(_('important'), default = False)
    reminder = models.BooleanField(_('reminder'), default = False)
    remind_time = models.DateTimeField(_('time of reminder'), blank = True, null = True)
    repeat = models.IntegerField(_('repeat'), blank = True, choices = REPEAT_SELECT, default = NONE)
    repeat_num = models.IntegerField(_('repeat num'), blank = True, default = 1)
    repeat_days = models.IntegerField(_('repeat days'), blank = True, default = 0)
    categories = models.TextField(_('categories'), blank = True, default = "")
    info = models.TextField(_('information'), blank = True, default = "")
    
    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return self.name

    def next_iteration(self):
        next = date.today()

        if self.start and (self.repeat == NONE):
            next = self.start
        elif self.start and (self.repeat != NONE):
            if (not self.last_compl):
                next = self.start
            else:
                if (self.repeat == DAILY):
                    next = self.last_compl + timedelta(1)
                elif (self.repeat == WEEKLY):
                    next = self.last_compl + timedelta(7)
                elif (self.repeat == MONTHLY):
                    d = self.last_compl.day
                    m = self.last_compl.month
                    y = self.last_compl.year
                    if (m < 12):
                        m += 1
                    else:
                        m = 1
                        y += 1
                    last_day = calendar.monthrange(y, m)[1]
                    if (d > last_day):
                        d = last_day
                    next = date(y, m, d)
                    if (next.day != self.start.day):
                        # Теперь попытаемся скорректировать день, чтобы он был как у стартовой даты
                        d = next.day
                        m = next.month
                        y = next.year
                        last_day = calendar.monthrange(next.year, next.month)[1]
                        if (last_day < self.start.day):
                            d = last_day
                        else:
                            d = self.start.day
                        next = date(y, m, d)
                elif (self.repeat == ANNUALLY):
                    d = self.last_compl.day
                    m = self.last_compl.month
                    y = self.last_compl.year
                    y += 1
                    last_day = calendar.monthrange(y, m)[1]
                    if (d > last_day): # 29.02.YYYY
                        d = last_day
                    next = date(y, m, d)

        if self.stop and next and (next > self.stop):
            next = None
        return next

    def d_termin(self):
        if self.start and self.repeat:
            return self.next_iteration()
        else:
            if self.stop:
                return self.stop
        return None

    def b_expired(self):
        d = self.d_termin()
        if d:
            return (d < date.today())
        return False

    def s_termin(self):
        d = self.d_termin()

        if not d:
            return ''

        if self.b_expired():
            s = str(_('expired')).capitalize() + ', '
        else:
            s = str(_('termin')).capitalize() + ': '
        return s + str(nice_date(d))
            
    def s_repeat(self):
        if (self.repeat == NONE):
            return ''
        if (self.repeat_num == 1):
            if (self.repeat == WORKDAYS):
                return REPEAT[WEEKLY][1].capitalize()
            return REPEAT[self.repeat][1].capitalize()
        
        return '{} {} {}'.format(_('once every').capitalize(), self.repeat_num, REPEAT_NAME[self.repeat])

    def repeat_s_days(self):
        if (self.repeat == WEEKLY):
            if (self.repeat_days == 0):
                return self.stop.strftime('%A')
            if (self.repeat_days == 1+2+4+8+16):
                return str(_('work days')).capitalize()
            ret = ''
            monday = datetime(2020, 7, 6, 0, 0)
            if (self.repeat_days & 1):
                ret += monday.strftime('%A')
            if (self.repeat_days & 2):
                if (ret != ''):
                    ret += ', '
                ret += (monday +timedelta(1)).strftime('%A')
            return ret
        return ''



class Param(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_param_user')
    cur_view = models.IntegerField(_('current view'), blank = True)
    myday_sort_mode = models.IntegerField(_('sorting mode for view "My day"'), blank = True, null = True)
    myday_sort_dir = models.BooleanField(_('sorting direction for view "My day"'), default = False)
    important_sort_mode = models.IntegerField(_('sorting mode for view "Important"'), blank = True, null = True)
    important_sort_dir = models.BooleanField(_('sorting direction for view "Important"'), default = False)
    planned_sort_mode = models.IntegerField(_('sorting mode for view "Planned"'), blank = True, null = True)
    planned_sort_dir = models.BooleanField(_('sorting direction for view "Planned"'), default = False)
    all_sort_mode = models.IntegerField(_('sorting mode for view "All"'), blank = True, null = True)
    all_sort_dir = models.BooleanField(_('sorting direction for view "All"'), default = False)
    completed_sort_mode = models.IntegerField(_('sorting mode for view "Completed"'), blank = True, null = True)
    completed_sort_dir = models.BooleanField(_('sorting direction for view "Completed"'), default = False)
    list_sort_mode = models.IntegerField(_('sorting mode for view "List"'), blank = True, null = True)
    list_sort_dir = models.BooleanField(_('sorting direction for view "List"'), default = False)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)
    details_mode = models.IntegerField(_('details mode'), blank = True, null = True)
    details_pk = models.IntegerField(_('details pk'), blank = True, null = True)


class Step(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('task'))
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    name = models.CharField(_('list name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)
    completed = models.BooleanField(_('step is completed'), default = False)

    class Meta:
        verbose_name = _('step')
        verbose_name_plural = _('steps')

    def __str__(self):
        return self.name

def user_directory_path(instance, filename):
    return 'uploads/user_{0}/{1}'.format(instance.user.id, filename)
    
class TaskFiles(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_file_user')
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('task'))
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)
    upload = models.FileField(upload_to = user_directory_path)
    name = models.CharField(_('file name'), max_length = 200, blank = True)
    ext = models.CharField(_('file type'), max_length = 50, blank = True)
    size = models.IntegerField(_('file size'), blank = True, null = True)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')

    def __str__(self):
        return self.upload.name


class PerGrp(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_period_user')
    grp_id = models.IntegerField(_('period group id'), blank = True, null = True)
    is_open = models.BooleanField(_('period group is open'), default = False)

    class Meta:
        verbose_name = _('period group')
        verbose_name_plural = _('period groups')

    def name(self):
        return GRPS_PLANNED[self.grp_id].capitalize()

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_subscription_user')
    token = models.CharField(_('user device token'), max_length = 200, blank = False)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def __str__(self):
        return self.user.username + ': ' + self.token

