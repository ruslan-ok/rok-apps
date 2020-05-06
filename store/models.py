from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from hier.models import Folder

#----------------------------------
# deprecated
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    code = models.CharField(_('code').capitalize(), max_length=100, blank = True)
    name = models.CharField(_('name').capitalize(), max_length=300)
    uuid = models.CharField(_('UUID').capitalize(), max_length=100, blank = True)
    creation = models.DateTimeField(_('creation time').capitalize(), default = timezone.now)
    last_mod = models.DateTimeField(_('last modification time').capitalize(), null = True)

    def __str__(self):
        return self.name

    def qty(self):
        return len(Entry.objects.filter(group = self.id))
 

#----------------------------------
class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    title = models.CharField(_('title').capitalize(), max_length=500)
    username = models.CharField(_('username').capitalize(), max_length=150, blank=True)
    value = models.CharField(_('value').capitalize(), max_length=128)
    url = models.CharField(_('URL').capitalize(), max_length=150, blank = True)
    notes = models.TextField(_('notes').capitalize(), blank = True, null = True)
    uuid = models.CharField(_('UUID').capitalize(), max_length=100, blank = True)
    creation = models.DateTimeField(_('creation time').capitalize(), default = timezone.now)
    last_mod = models.DateTimeField(_('last modification time').capitalize(), null = True)
    group = models.ForeignKey(Group, verbose_name = _('group').capitalize(), on_delete = models.CASCADE, null = True)
    actual = models.IntegerField(_('actual').capitalize(), default = 1)

    def __str__(self):
        return self.name

    def have_notes(self):
        if (self.notes == None) or (self.notes == ''):
            return ''
        else:
            return '@'

#----------------------------------
# deprecated
class History(models.Model):
    node = models.ForeignKey(Entry, verbose_name = _('node').capitalize(), on_delete = models.CASCADE, related_name='node')
    data = models.ForeignKey(Entry, verbose_name = _('entry').capitalize(), on_delete = models.CASCADE, related_name='data')

    def __str__(self):
        return self.node.name


#----------------------------------
class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='store_user')
    #deprecated
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null = True, verbose_name=_('group filter'), blank = True)
    ln = models.IntegerField(_('length').capitalize(), default = 20)
    uc = models.BooleanField(_('upper case').capitalize(), default = True)
    lc = models.BooleanField(_('lower case').capitalize(), default = True)
    dg = models.BooleanField(_('digits').capitalize(), default = True)
    sp = models.BooleanField(_('special symbols').capitalize(), default = True)
    br = models.BooleanField(_('brackets').capitalize(), default = True)
    mi = models.BooleanField(_('minus').capitalize(), default = True)
    ul = models.BooleanField(_('underline').capitalize(), default = True)
    ac = models.BooleanField(_('avoid confusion').capitalize(), default = True)

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')


