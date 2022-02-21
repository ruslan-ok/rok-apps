from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from todo.models import Lst
from hier.models import Lst

app_name = 'store'

#----------------------------------
# deprecated
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    code = models.CharField(_('code'), max_length=100, blank = True)
    name = models.CharField(_('name'), max_length=300)
    uuid = models.CharField(_('UUID'), max_length=100, blank = True)
    creation = models.DateTimeField(_('creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), null = True, auto_now = True)

#----------------------------------
class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    title = models.CharField(_('title'), max_length=500)
    username = models.CharField(_('username'), max_length=150, blank=True)
    value = models.CharField(_('value'), max_length=128)
    url = models.CharField(_('URL'), max_length=2000, blank = True)
    notes = models.TextField(_('notes'), blank = True, null = True)
    uuid = models.CharField(_('UUID'), max_length=100, blank = True)
    created = models.DateTimeField(_('creation time'), auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)
    # group - deprecated
    group = models.ForeignKey(Group, verbose_name = _('group'), on_delete = models.CASCADE, null = True)
    actual = models.IntegerField(_('actual'), default = 1)
    categories = models.CharField(_('categories'), max_length = 2000, blank = True, default = '', null = True)
    params = models.IntegerField(_('generator parameters used'), default = 0, null = True)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)

#----------------------------------
# deprecated
class History(models.Model):
    node = models.ForeignKey(Entry, verbose_name = _('node'), on_delete = models.CASCADE, related_name='node')
    data = models.ForeignKey(Entry, verbose_name = _('entry'), on_delete = models.CASCADE, related_name='data')

#----------------------------------
class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='store_user')
    ln = models.IntegerField(_('length').capitalize(), default = 20)
    uc = models.BooleanField(_('upper case').capitalize(), default = True)
    lc = models.BooleanField(_('lower case').capitalize(), default = True)
    dg = models.BooleanField(_('digits').capitalize(), default = True)
    sp = models.BooleanField(_('special symbols').capitalize(), default = True)
    br = models.BooleanField(_('brackets').capitalize(), default = True)
    mi = models.BooleanField(_('minus').capitalize(), default = True)
    ul = models.BooleanField(_('underline').capitalize(), default = True)
    ac = models.BooleanField(_('avoid confusion').capitalize(), default = True)
    un = models.CharField(_('default username'), max_length=160, blank=True, default='')


