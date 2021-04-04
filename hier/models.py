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
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'visit_user')
    stamp = models.DateTimeField(_('visit time'), null = False)
    url = models.CharField(_('visited url'), max_length=200, blank = True)
    app = models.CharField(_('visited application'), max_length=200, blank = True)
    page = models.CharField(_('visited page'), max_length=200, blank = True)
    info = models.CharField(_('page info'), max_length=200, blank = True)

    class Meta:
        verbose_name = _('visited page')
        verbose_name_plural = _('visited pages')

    def __str__(self):
        return self.app + ' - ' + self.page
    
    def title(self):
        if not self.page and not self.info:
            title = ''
        if self.page and not self.info:
            title = _(self.page).capitalize()
        if not self.page and self.info:
            title = self.info
        if self.page and self.info:
            title = '{} [{}]'.format(_(self.page).capitalize(), self.info)
        if not title:
            return _(self.app).capitalize()
        else:
            return _(self.app).capitalize() + ' - ' + title
        
    def reverse_url(self):
        return self.url
        
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


class IPInfo(models.Model):
    ip = models.CharField('IP', max_length=20, blank=False)
    success = models.BooleanField('success', default=False, null=True)
    ip_type = models.CharField('type', max_length=100, blank=True, null=True)
    continent = models.CharField('continent', max_length=100, blank=True, null=True)
    continent_code = models.CharField('continent_code', max_length=10, blank=True, null=True)
    country = models.CharField('country name', max_length=100, blank=True, null=True)
    country_code = models.CharField('country_code', max_length=3, blank=True, null=True)
    country_flag = models.CharField('country_flag', max_length=1000, blank=True, null=True)
    country_capital = models.CharField('country_capital', max_length=100, blank=True, null=True)
    country_phone = models.CharField('country_phone', max_length=100, blank=True, null=True)
    country_neighbours = models.CharField('country_neighbours', max_length=100, blank=True, null=True)
    region = models.CharField('region', max_length=100, blank=True, null=True)
    city = models.CharField('city', max_length=100, blank=True, null=True)
    latitude = models.CharField('latitude', max_length=100, blank=True, null=True)
    longitude = models.CharField('longitude', max_length=100, blank=True, null=True)
    asn = models.CharField('asn', max_length=100, blank=True, null=True)
    org = models.CharField('org', max_length=100, blank=True, null=True)
    timezone_dstOffset = models.CharField('timezone_dstOffset', max_length=10, blank=True, null=True)
    timezone_gmtOffset = models.CharField('timezone_gmtOffset', max_length=100, blank=True, null=True)
    timezone_gmt = models.CharField('timezone_gmt', max_length=100, blank=True, null=True)
    currency = models.CharField('currency', max_length=100, blank=True, null=True)
    currency_code = models.CharField('currency_code', max_length=100, blank=True, null=True)
    currency_symbol = models.CharField('currency_symbol', max_length=100, blank=True, null=True)
    
    def info(self):
        ret = ''
        if self.country_code:
            ret = self.country_code
        if self.country:
            if ret:
                ret += ', '
            ret += self.country
        if self.city:
            if ret:
                ret += ', '
            ret += self.city
        if self.org:
            if ret:
                ret += ' - '
            ret += self.org
        if self.ip:
            if ret:
                ret += ' - '
            ret += self.ip
        return ret

class AccessLog(models.Model):
    host = models.ForeignKey(IPInfo, on_delete = models.CASCADE, verbose_name='IP address', related_name='Host_IP', null=True)
    user = models.CharField('user', max_length=200, blank=True)
    event = models.DateTimeField('event time', null=False)
    method = models.CharField('method', max_length=100, blank=True)
    uri = models.CharField('uri', max_length=1000, blank=True)
    protocol = models.CharField('protocol', max_length=100, blank=True)
    status = models.IntegerField('status', blank=True, null=True)
    size = models.IntegerField('request size', blank=True, null=True)
    
    def __repr__(self):
        return str(self.id) + ' [' + str(self.event) + ']'

class SiteStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    record = models.ForeignKey(AccessLog, on_delete = models.RESTRICT, verbose_name='log record', related_name='LogID', null=True)

