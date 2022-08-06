import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from task.const import APP_TODO

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

DEVICE = os.environ.get('DJANGO_DEVICE')

class EventType(models.TextChoices):
        ERROR = 'error', _('Error')
        WARNING = 'warning', _('Warning')
        INFO = 'info', _('Information')
        DEBUG = 'debug', _('Debug')
        
class ServiceEvent(models.Model):
    device = models.CharField(_('Device name'), max_length=50, blank=True, default=DEVICE, null=True)
    app = models.CharField(_('App name'), max_length=50, blank=False, default=APP_TODO, null=True)
    service = models.CharField(_('Service name'), max_length=50, blank=False, null=True)
    created = models.DateTimeField(_('Creation time'), blank=True, default=datetime.now)
    type = models.CharField(_('Event type'), max_length=20, blank=False, choices=EventType.choices, default=EventType.INFO)
    name = models.CharField(_('Event name'), max_length=200, blank=False)
    info = models.TextField(_('Event description'), blank=True, null=True)

    def __repr__(self):
        return f'{self.app}:{self.service} [{self.created.strftime("%Y-%m-%d %H:%M:%S")}] {self.type} | {self.name} - {self.info}'
    
    def s_info(self):
        if self.info:
            return self.info
        return ''