import urllib
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    creation = models.DateTimeField(_('Creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('Last modification time'), null = True, auto_now = True)
    name = models.CharField(_('Name'), max_length=1000)
    path = models.CharField(_('Path'), max_length=1000, blank = True)
    categories = models.CharField(_('Categories'), max_length=1000, blank = True)
    info = models.TextField(_('Information'), blank = True)
    lat = models.DecimalField(_('Latitude'), max_digits = 9, decimal_places = 6, null = True)
    lon = models.DecimalField(_('Longitude'), max_digits = 9, decimal_places = 6, null = True)
    size = models.IntegerField(_('Size'), null = True)

    def __str__(self):
        return self.name

    def __repr__(self):
        subdir = ''
        if self.path:
            subdir = self.path + '/'
        url = urllib.parse.quote_plus(subdir + self.name)
        return '{ url: ' + url + ', sz: ' + str(self.size) + ' }'

    def full_name(self):
        if self.path:
            return self.path + '/' + self.name
        return self.name

    def subdir(self):
        if self.path:
            return self.path + '/'
        return ''
