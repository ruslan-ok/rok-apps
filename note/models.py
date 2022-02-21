from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from todo.models import Lst

app_name = 'note'

#----------------------------------
class Note(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name  = models.CharField(_('name'), max_length = 200, blank = False)
    code  = models.CharField(_('code'), max_length = 200, blank = True)
    descr = models.TextField(_('description'), blank = True)
    publ  = models.DateTimeField(_('publication date'), blank=True, default = datetime.now)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    url = models.CharField(_('URL'), max_length=2000, blank = True)
    categories = models.CharField(_('categories'), max_length = 2000, blank = True, default = '', null = True)
    kind  = models.CharField(_('kind of note'), max_length = 200, blank = True, default = 'note')

