from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    node = models.IntegerField(_('node').capitalize(), null = True)
    code = models.CharField(_('code').capitalize(), max_length=500, blank = True)
    name = models.CharField(_('name').capitalize(), max_length=1000)
    creation = models.DateTimeField(_('creation time').capitalize(), default = timezone.now)
    last_mod = models.DateTimeField(_('last modification time').capitalize(), null = True)
    is_open = models.BooleanField(_('node is opened').capitalize(), default = False)
    icon = models.CharField(_('icon').capitalize(), max_length=50, blank = True)
    color = models.CharField(_('color'), max_length = 20, blank = True)
    model_name = models.CharField(_('application entity name').capitalize(), max_length=50, blank = True)
    # deprecated. use get_folder_enabled
    folder_enabled = models.BooleanField(_('enable folders in items list').capitalize(), default = False)
    content_id = models.IntegerField(_('content id').capitalize(), default = 0)

    def __str__(self):
        return self.name

    def lightness(self):
        if not self.color:
            return 0
        value = self.color.lstrip('#')
        lv = len(value)
        rgb = tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))
        return (rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722) / 255

    def use_black(self):
        return (self.lightness() > 0.6)

    def get_folder_enabled(self):
        if (self.model_name == '') or (self.model_name == 'trash') or (self.model_name == 'note:note'):
            return True
        return False

