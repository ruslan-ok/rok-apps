from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    creation = models.DateTimeField(_('creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), null = True, auto_now = True)
    name = models.CharField(_('name'), max_length=1000)
    path = models.CharField(_('path'), max_length=1000, blank = True)
    categories = models.CharField(_('categories'), max_length=1000, blank = True)
    info = models.TextField(_('information'), blank = True)
    lat = models.DecimalField(_('latitude').capitalize(), max_digits = 9, decimal_places = 6, null = True)
    lon = models.DecimalField(_('longitude').capitalize(), max_digits = 9, decimal_places = 6, null = True)
    size = models.IntegerField(_('size').capitalize(), null = True)
