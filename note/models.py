from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

#----------------------------------
# deprecated
class List(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name    = models.CharField(_('name'), max_length = 200, blank = False)
    code    = models.CharField(_('code'), max_length = 50, blank = True)
    color   = models.CharField(_('color'), max_length = 20, blank = True)
    comment = models.CharField(_('description'), max_length = 2000, blank = True)

    class Meta:
        verbose_name = _('notes list')
        verbose_name_plural = _('notes lists')

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return self.code + ': ' + self.name

#----------------------------------
class Note(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name  = models.CharField(_('name'), max_length = 200, blank = False)
    code  = models.CharField(_('code'), max_length = 200, blank = True)
    descr = models.TextField(_('description'), blank = True)
    # deprecated
    list  = models.ForeignKey(List, on_delete=models.CASCADE, blank = True, null = True, verbose_name=_('list'))
    publ  = models.DateTimeField(_('publication date'), blank=True, default = datetime.now)

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    def __str__(self):
        return self.name


#----------------------------------
# deprecated
class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length = 200, blank = False)
    code = models.CharField(_('code'), max_length = 200, blank = True, default = '')
    chrono = models.BooleanField(_('chronological list of entries'), default = False)

    class Meta:
        verbose_name = _('notes view')
        verbose_name_plural = _('notes views')

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return self.code + ': ' + self.name

#----------------------------------
# deprecated
class Filter(models.Model):
    view   = models.ForeignKey(View, on_delete=models.CASCADE, verbose_name=_('view'))
    entity = models.IntegerField(_('entity'), default = 0)
    npp    = models.IntegerField(_('sort number'), default = 0)
    value  = models.IntegerField(_('value'), default = 0)

    class Meta:
        verbose_name = _('view filter')
        verbose_name_plural = _('view filters')


#----------------------------------
# deprecated
class Param(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='notes_user')
    view = models.ForeignKey(View, on_delete=models.CASCADE, null = True, verbose_name=_('view'))

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')



