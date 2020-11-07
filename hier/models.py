from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from todo.models import Lst

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

# Параметры сайта в целом
# deprecated
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
        return self.user.username + ' - ' + self.cur_view


# Параметры приложений
class AppParam(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'params_user')
    app = models.CharField(_('application'), max_length = 50)
    aside = models.BooleanField(_('aside visible'), default = False)
    article = models.BooleanField(_('article visible'), default = False)
    content = models.CharField(_('kind of objects in page'), max_length = 1000, blank = True)
    kind = models.CharField(_('kind of object in article'), max_length = 50, blank = True)
    lst = models.ForeignKey(Lst, on_delete = models.CASCADE, verbose_name = _('list'), blank = True, null = True)
    art_id = models.IntegerField(_('entity id for article'), blank = True, null = True)
    sort = models.CharField(_('sorting mode'), max_length = 1000, blank = True)
    reverse = models.BooleanField(_('reverse sorting'), default = False)
    restriction = models.CharField(_('filter mode'), max_length = 1000, blank = True)

    class Meta:
        verbose_name = _('user parameters')
        verbose_name_plural = _('users parameters')

    def __str__(self):
        return self.user.username + ' - ' + self.app + ':' + self.kind

#----------------------------------
def get_app_params(user, app):
    if not user.is_authenticated:
        return None

    if not AppParam.objects.filter(user = user.id, app = app).exists():
        return AppParam.objects.create(user = user, app = app, aside = False, article = False, content = '', kind = '', lst = None, art_id = 0)

    return AppParam.objects.filter(user = user.id, app = app).get()


# Параметры приложений
class VisitedHistory(models.Model):
    stamp = models.DateTimeField(_('visit time'), null = False)
    app = models.CharField(_('visited application'), max_length=200, blank = True)
    page = models.CharField(_('visited page'), max_length=200, blank = True)
    url = models.CharField(_('visited url'), max_length=200, blank = True)

    class Meta:
        verbose_name = _('visited page')
        verbose_name_plural = _('visited pages')

    def __str__(self):
        return self.app + ' - ' + self.page

# Группы записей контента приложения
class ContentGroup(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'content_groups_user')
    app = models.CharField(_('application'), max_length=200, blank = True)
    name = models.CharField(_('name'), max_length=1000, blank = True)
    grp_id = models.IntegerField(_('period group id'), blank = True, null = True)
    is_open = models.BooleanField(_('period group is open'), default = False)

    class Meta:
        verbose_name = _('content records group')
        verbose_name_plural = _('content records groups')

    def __str__(self):
        return self.app + ':' + self.name

def toggle_content_group(user_id, app, grp_id):
    if ContentGroup.objects.filter(user = user_id, app = app, grp_id = grp_id).exists():
        grp = ContentGroup.objects.filter(user = user_id, app = app, grp_id = grp_id).get()
        grp.is_open = not grp.is_open
        grp.save()
