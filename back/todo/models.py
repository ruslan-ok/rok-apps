from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from core.models import Item as CoreItem
from task.const import *

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'todo_subscription_user')
    token = models.CharField(_('user device token'), max_length = 200, blank = False)

class Item(CoreItem):
    completed = models.BooleanField(_('Completed'), default=False, null=True)
    completion = models.DateTimeField(_('Completion time'), blank=True, null=True)
    in_my_day = models.BooleanField(_('In My day'), default=False, null=True)
    important = models.BooleanField(_('Important'), default=False, null=True)
    remind = models.DateTimeField(_('Remind'), blank=True, null=True)
    first_remind = models.DateTimeField(_('First remind'), blank=True, null=True)
    last_remind = models.DateTimeField(_('Last remind'), blank=True, null=True)
    repeat = models.IntegerField(_('Repeat'), blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    repeat_num = models.IntegerField(_('Repeat num'), blank=True, null=True)
    repeat_days = models.IntegerField(_('Repeat days'), blank=True, null=True)
