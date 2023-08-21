from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
CURRENT = 1
HISTORICAL = 2
FORECASTED_HOURLY = 3
FORECASTED_DAILY = 4

EVENT_TYPE = [
    (CURRENT, _('current')),
    (HISTORICAL, _('historical')),
    (FORECASTED_HOURLY, _('forecasted hourly')),
    (FORECASTED_DAILY, _('forecasted daily')),
]

class Weather(models.Model):
    event = models.DateTimeField('Date and time of the described event', blank=True, null=True)
    fixed = models.DateTimeField('Date and time when this event is described', blank=True, null=True)
    ev_type = models.IntegerField('Event type: current, historical, forecasted', null=False, choices=EVENT_TYPE, default=CURRENT)
    lat = models.CharField('Latitude', max_length=10, blank=True)
    lon = models.CharField('Longitude', max_length=10, blank=True)
    elevation = models.IntegerField('Elevation', null=True)
    timezone = models.CharField('Timezone', max_length=20, blank=True)
    units = models.CharField('Units', max_length=10, blank=True)
    weather = models.CharField('String identifier of the weather icon', max_length=20, blank=True)
    icon = models.IntegerField('Numeric identifier of the weather icon', null=True)
    summary = models.CharField('Summary', max_length=200, blank=True)
    temperature = models.DecimalField('Temperature', null=True, max_digits=5, decimal_places=1)
    temperature_min = models.DecimalField('Temperature min', null=True, max_digits=5, decimal_places=1)
    temperature_max = models.DecimalField('Temperature max', null=True, max_digits=5, decimal_places=1)
    wind_speed = models.DecimalField('Wind speed', null=True, max_digits=5, decimal_places=1)
    wind_angle = models.IntegerField('Wind angle', null=True)
    wind_dir = models.CharField('Wind direction', max_length=5, blank=True)
    prec_total = models.DecimalField('Precipitation total', null=True, max_digits=10, decimal_places=1)
    prec_type = models.CharField('Precipitation type', max_length=10, blank=True)
    cloud_cover = models.IntegerField('Cloud cover', null=True)

class CurrencyRate(models.Model):
    currency = models.CharField('Currency', max_length=10, blank=False)
    base = models.CharField('Base currency', max_length=10, blank=True, default='USD')
    date = models.DateField('Rate Date', blank=False, null=False)
    num_units = models.IntegerField('Number of units exchanged', null=False, default=1)
    value = models.DecimalField('Exchange rate to USD', blank=True, null=True, max_digits=15, decimal_places=4)
    source = models.CharField('Data source', max_length=200, blank=True)
    info = models.CharField('Comment', max_length=1000, blank=True)

class CurrencyApis(models.Model):
    name = models.CharField('Name', max_length=100, blank=False)
    prioritet = models.IntegerField('Prioritet', default=1, null=False)
    api_url = models.CharField('URL for rate on date', max_length=1000, blank=False)
    token = models.CharField('Phrase for exhausted limit', max_length=1000, blank=True)
    value_path = models.CharField('json path to value', max_length=1000, blank=True)
    phrase = models.CharField('Phrase for exhausted limit', max_length=1000, blank=True)
    next_try = models.DateField('Next try Date', null=True)
    today_avail = models.BooleanField('Today rate is available', null=True, default=True)
