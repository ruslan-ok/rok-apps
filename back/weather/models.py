from django.db import models

class Place(models.Model):
    place_id = models.CharField('place_id', max_length=200, blank=False)
    name = models.CharField('name', max_length=100, blank=False)
    adm_area1 = models.CharField('adm_area1', max_length=100, blank=True, null=True)
    adm_area2 = models.CharField('adm_area2', max_length=100, blank=True, null=True)
    country = models.CharField('country', max_length=100, blank=True)
    lat = models.CharField('lat', max_length=12, blank=True)
    lon = models.CharField('lon', max_length=12, blank=True)
    timezone = models.CharField('timezone', max_length=100, blank=True)
    type = models.CharField('type', max_length=100, blank=True)
    search_name = models.CharField('search_name', max_length=100, blank=True)
    lat_cut = models.CharField('lat_cut', max_length=12, blank=True)
    lon_cut = models.CharField('lon_cut', max_length=12, blank=True)

class AstroData(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name='place', related_name='astro_place')
    date = models.DateField('Date of the astro events', blank=False, null=False)
    day_length = models.IntegerField('Length of the day', null=True)
    sunrise = models.DateTimeField('Sunrise', blank=True, null=True)
    sunset = models.DateTimeField('Sunset', blank=True, null=True)
    solar_noon = models.DateTimeField('Solar noon', blank=True, null=True)
    civil_twilight_begin = models.DateTimeField('Civil twilight begin', blank=True, null=True)
    civil_twilight_end = models.DateTimeField('Civil twilight end', blank=True, null=True)
    nautical_twilight_begin = models.DateTimeField('Nautical twilight begin', blank=True, null=True)
    nautical_twilight_end = models.DateTimeField('Nautical twilight end', blank=True, null=True)
    astronomical_twilight_begin = models.DateTimeField('Astronomical twilight begin', blank=True, null=True)
    astronomical_twilight_end = models.DateTimeField('Astronomical twilight end', blank=True, null=True)

    class Meta:
        unique_together = ('place', 'date')

CURRENT = 1
HISTORICAL = 2
FORECASTED_HOURLY = 3
FORECASTED_DAILY = 4

EVENT_TYPE = [
    (CURRENT, 'current'),
    (HISTORICAL, 'historical'),
    (FORECASTED_HOURLY, 'forecasted hourly'),
    (FORECASTED_DAILY, 'forecasted daily'),
]

class Forecast(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name='place', related_name='forecast_place')
    fixed = models.DateTimeField('Date and time when this event is described', blank=True, null=True)
    ev_type = models.IntegerField('Event type: current, historical, forecasted', null=False, choices=EVENT_TYPE, default=CURRENT)
    event = models.DateTimeField('Date and time of the described event', blank=True, null=True)
    lat = models.CharField('Latitude', max_length=10, blank=True)
    lon = models.CharField('Longitude', max_length=10, blank=True)
    location = models.CharField('Location', max_length=200, blank=True)
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

    class Meta:
        unique_together = ('place', 'fixed', 'ev_type', 'event')

    def __repr__(self):
        type = '?'
        match self.ev_type:
            case 1: type = 'CURRENT'
            case 2: type = 'HISTORICAL'
            case 3: type = 'HOURLY'
            case 4: type = 'DAILY'
        return self.place.name + ': ' + type + ' ' + str(self.event)
