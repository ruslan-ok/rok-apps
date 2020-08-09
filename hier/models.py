from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    node = models.IntegerField(_('node'), null = True)
    code = models.CharField(_('code'), max_length=500, blank = True)
    name = models.CharField(_('name'), max_length=1000)
    creation = models.DateTimeField(_('creation time'), default = datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), null = True)
    is_open = models.BooleanField(_('node is opened'), default = False)
    icon = models.CharField(_('icon'), max_length=50, blank = True)
    color = models.CharField(_('color'), max_length = 20, blank = True)
    model_name = models.CharField(_('application entity name'), max_length=50, blank = True)
    # deprecated. use get_folder_enabled
    folder_enabled = models.BooleanField(_('enable folders in items list'), default = False)
    content_id = models.IntegerField(_('content id'), default = 0)
    is_folder = models.BooleanField(_('node is folder'), default = False)

    class Meta:
        verbose_name = _('folder')
        verbose_name_plural = _('folders')

    def __str__(self):
        return self.name

    def lightness(self):
        if not self.color:
            return 0
        if (len(self.color) != 7):
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

class Param(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    folder_id = models.IntegerField(_('folder id'), null = True)
    aside = models.BooleanField(_('aside visible'), default = False)
    article = models.BooleanField(_('article visible'), default = False)
    cur_app = models.CharField(_('current application'), max_length=50, blank = True)
    cur_view = models.CharField(_('current view'), max_length=50, blank = True)
    article_mode = models.CharField(_('article mode'), max_length=50, blank = True)
    article_pk = models.IntegerField(_('article pk'), blank = True, null = True)
    last_url = models.CharField(_('last visited url'), max_length=200, blank = True)
    last_app = models.CharField(_('last visited app'), max_length=200, blank = True)
    last_page = models.CharField(_('last visited page'), max_length=200, blank = True)

    class Meta:
        verbose_name = _('user parameters')
        verbose_name_plural = _('users parameters')

    def __str__(self):
        return self.user.name + ' - ' + cur_view

