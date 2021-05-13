from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from task.const import *

class TaskGrp(models.Model):
    """
    Task groups
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    app = models.CharField(_('application name'), max_length = 50, blank = False, default = 'todo', null = True)
    node = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name=_('node'), blank=True, null=True)
    name = models.CharField(_('group name'), max_length=200, blank=False)
    sort = models.CharField(_('sort code'), max_length=50, blank=True)
    is_open = models.BooleanField(_('node is open'), default=False)
    is_leaf = models.BooleanField(_('node is leaf'), default=True)
    created = models.DateTimeField(_('creation time'), blank=True, auto_now_add=True)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)

    class Meta:
        verbose_name=_('task group')
        verbose_name_plural = _('task groups')

    def __str__(self):
        return self.name

class ATask(models.Model):
    """
    An Entity that can be a Task or something else
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'task_user')
    grp = models.ForeignKey(TaskGrp, on_delete=models.CASCADE, verbose_name=_('group'), blank=True, null=True)
    name = models.CharField(_('name'), max_length=200, blank=False)
    start = models.DateField(_('start date'), blank=True, null=True)
    stop = models.DateField(_('termin'), blank=True, null=True)
    completed = models.BooleanField(_('completed'), default=False)
    completion = models.DateTimeField(_('completion time'), blank=True, null=True, default=None)
    in_my_day = models.BooleanField(_('in my day'), default=False)
    important = models.BooleanField(_('important'), default=False)
    remind = models.DateTimeField(_('remind'), blank=True, null=True)
    last_remind = models.DateTimeField(_('last remind'), blank=True, null=True)
    repeat = models.IntegerField(_('repeat'), blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    repeat_num = models.IntegerField(_('repeat num'), blank=True, default=1)
    repeat_days = models.IntegerField(_('repeat days'), blank=True, default=0)
    categories = models.TextField(_('categories'), blank=True, default="")
    info = models.TextField(_('information'), blank=True, default="")
    app_task = models.IntegerField(_('role in application Task'), choices=TASK_ROLE_CHOICE, default=NONE, null=True)
    app_note = models.IntegerField(_('role in application Note'), choices=NOTE_ROLE_CHOICE, default=NONE, null=True)
    app_news = models.IntegerField(_('role in application News'), choices=NEWS_ROLE_CHOICE, default=NONE, null=True)
    app_store = models.IntegerField(_('role in application Store'), choices=STORE_ROLE_CHOICE, default=NONE, null=True)
    app_doc = models.IntegerField(_('role in application Document'), choices=DOC_ROLE_CHOICE, default=NONE, null=True)
    app_warr = models.IntegerField(_('role in application Warranty'), choices=WARR_ROLE_CHOICE, default=NONE, null=True)
    app_expen = models.IntegerField(_('role in application Expense'), choices=EXPEN_ROLE_CHOICE, default=NONE, null=True)
    app_trip = models.IntegerField(_('role in application Trip'), choices=TRIP_ROLE_CHOICE, default=NONE, null=True)
    app_fuel = models.IntegerField(_('role in application Fueling'), choices=FUEL_ROLE_CHOICE, default=NONE, null=True)
    app_apart = models.IntegerField(_('role in application Communal'), choices=APART_ROLE_CHOICE, default=NONE, null=True)
    app_health = models.IntegerField(_('role in application Health'), choices=HEALTH_ROLE_CHOICE, default=NONE, null=True)
    app_work = models.IntegerField(_('role in application Work'), choices=WORK_ROLE_CHOICE, default=NONE, null=True)
    app_photo = models.IntegerField(_('role in application Photo Bank'), choices=PHOTO_ROLE_CHOICE, default=NONE, null=True)
    created = models.DateTimeField(_('creation time'), auto_now_add=True)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)

    class Meta:
        verbose_name=_('task')
        verbose_name_plural = _('tasks')

    def get_url(self):
        return reverse('task-detail', args=[self.id])
    
    def marked_item(self):
        return self.completed

    
class ContentGrp(models.Model):
    """
    Groups of content records of the Application
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'content_grps_user')
    app = models.CharField(_('application'), max_length=200, blank=True)
    name = models.CharField(_('name'), max_length=1000, blank=True)
    grp_id = models.IntegerField(_('period group id'), blank=True, null=True)
    is_open = models.BooleanField(_('period group is open'), default=False)

    class Meta:
        verbose_name=_('content records group')
        verbose_name_plural = _('content records groups')

    def __str__(self):
        return self.app + ':' + self.name

def toggle_content_group(user_id, app, grp_id):
    if ContentGroup.objects.filter(user = user_id, app = app, grp_id = grp_id).exists():
        grp = ContentGroup.objects.filter(user = user_id, app = app, grp_id = grp_id).get()
        grp.is_open = not grp.is_open
        grp.save()

class TaskUrls(models.Model):
    task = models.ForeignKey(ATask, on_delete=models.CASCADE, verbose_name=_('task'), related_name = 'task_urlsr')
    num = models.IntegerField(_('sort number'), default=0, null=True)
    href = models.CharField(_('URL'), max_length=2000, blank=True)

class AAppParam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'app_params_user')
    app = models.CharField(_('application'), max_length=50)
    view = models.CharField(_('view'), max_length=50, blank=True, null=True)
    grp = models.ForeignKey(TaskGrp, on_delete=models.CASCADE, verbose_name=_('group'), blank=True, null=True)
    art_id = models.IntegerField(_('entity id for article'), blank=True, null=True)
    sort = models.CharField(_('sorting mode'), max_length=1000, blank=True)
    reverse = models.BooleanField(_('reverse sorting'), default=False)
    restriction = models.CharField(_('filter mode'), max_length=1000, blank=True)
    beta = models.BooleanField(_('beta version'), default=False)
    class Meta:
        verbose_name=_('user parameters')
        verbose_name_plural = _('users parameters')

    