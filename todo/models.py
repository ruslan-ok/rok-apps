from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from task.const import APP_TODO

app_name = 'todo'

class Grp(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    app = models.CharField(_('application name'), max_length = 50, blank = False, default = APP_TODO, null = True)
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    node = models.ForeignKey('self', on_delete = models.CASCADE, verbose_name = _('node'), blank = True, null = True)
    name = models.CharField(_('group name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)
    is_open = models.BooleanField(_('node is open'), default = False)

class Lst(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    app = models.CharField(_('application name'), max_length = 50, blank = False, default = APP_TODO, null = True)
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    grp = models.ForeignKey(Grp, on_delete = models.CASCADE, verbose_name = _('group'), blank = True, null = True)
    name = models.CharField(_('list name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)

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
    stop = models.DateField(_('termin'), blank = True, null = True)
    completed = models.BooleanField(_('completed'), default = False)
    completion = models.DateTimeField(_('completion time'), blank = True, null = True, default = None)
    in_my_day = models.BooleanField(_('in my day'), default = False)
    important = models.BooleanField(_('important'), default = False)
    remind = models.DateTimeField(_('remind'), blank = True, null = True)
    last_remind = models.DateTimeField(_('last remind'), blank = True, null = True)
    repeat = models.IntegerField(_('repeat'), blank = True, null = True, choices = REPEAT_SELECT, default = NONE)
    repeat_num = models.IntegerField(_('repeat num'), blank = True, default = 1)
    repeat_days = models.IntegerField(_('repeat days'), blank = True, default = 0)
    categories = models.TextField(_('categories'), blank = True, default = "")
    info = models.TextField(_('information'), blank = True, default = "")
    url = models.CharField(_('url'), max_length = 2000, blank = True)

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

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_subscription_user')
    token = models.CharField(_('user device token'), max_length = 200, blank = False)

