from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    node = models.IntegerField(_('node').capitalize(), null = True)
    code = models.CharField(_('code').capitalize(), max_length=500, blank = True)
    name = models.CharField(_('name').capitalize(), max_length=1000)
    creation = models.DateTimeField(_('creation time').capitalize(), default = timezone.now)
    last_mod = models.DateTimeField(_('last modification time').capitalize(), null = True)
    notes = models.TextField(_('notes').capitalize(), blank = True, null = True)
    qty = models.IntegerField(_('number of nested elements').capitalize(), default = 0)
    storage = models.IntegerField(_('storage type').capitalize(), default = 0)
    ext = models.CharField(_('entry extension').capitalize(), max_length=50, blank = True)
    content = models.IntegerField(_('link to content').capitalize(), default = 0)
    is_open = models.BooleanField(_('node is opened').capitalize(), default = False)
    icon = models.CharField(_('icon').capitalize(), max_length=50, blank = True)
    app = models.CharField(_('application').capitalize(), max_length=50, blank = True)

    def __str__(self):
        return self.name
