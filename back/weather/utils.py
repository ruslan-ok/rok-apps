import os, requests, json
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil import tz
from weather.models import Place, AstroData, Forecast, CURRENT, FORECASTED_DAILY, FORECASTED_HOURLY

astro_api = 'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted={formatted}'
find_places_prefix_api = 'https://www.meteosource.com/api/v1/free/find_places_prefix?text={text}&key={key}'
nearest_place_api = 'https://www.meteosource.com/api/v1/free/nearest_place?lat={lat}&lon={lon}&key={key}'
forecast_api = 'https://www.meteosource.com/api/v1/free/point?place_id={place_id}&sections=all&timezone={timezone}&language=en&units=auto&key={key}'

class WeatherError(Exception):
    pass

def get_api_chart_data(location: str, lat: str, lon: str) -> dict:
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=weather&version=v2&location=' + location + '&lat=' + lat + '&lon=' + lon, headers=headers, verify=verify)
    if (resp.status_code != 200):
        raise WeatherError('get_api_chart_data', f'Bad response status code: {resp.status_code}')
    ret = json.loads(resp.content)
    return ret

def get_place(location: str, lat: str, lon: str) -> Place:
    if location:
        if Place.objects.filter(search_name=location).exists():
            place = Place.objects.filter(search_name=location).get()
            return place
        headers = {'accept': 'application/json'}
        token = os.getenv('API_WEATHER_KEY', '')
        url = find_places_prefix_api.replace('{text}', location).replace('{key}', token)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise WeatherError('get_place', f'(1) Bad response status code: {resp.status_code}')
        ret = json.loads(resp.content)
        if type(ret) == list:
            if len(ret) > 1:
                tmp = [x for x in ret if x['country'] in ('Republic of Belarus', 'Poland')]
                if len(tmp) > 0:
                    ret = tmp[0]
        if type(ret) == list and len(ret) > 0:
            ret = ret[0]
        if type(ret) != dict:
            raise WeatherError('get_place', f'Wrong type of response data: {ret}')
        place = Place.objects.create(
            place_id = ret['place_id'],
            name = ret['name'],
            adm_area1 = ret['adm_area1'],
            adm_area2 = ret['adm_area2'],
            country = ret['country'],
            lat = ret['lat'],
            lon = ret['lon'],
            timezone = ret['timezone'],
            type = ret['type'],
            search_name = location,
            lat_cut = '',
            lon_cut = '',
        )
        return place

    if not lat or not lon:
        raise WeatherError('get_place', 'Empty parameters "location", "lat", "lon".')

    lat_cut = lat[:5] + '00000'
    lon_cut = lon[:5] + '00000'
    if Place.objects.filter(lat_cut=lat_cut, lon_cut=lon_cut).exists():
        place = Place.objects.filter(lat_cut=lat_cut, lon_cut=lon_cut).get()
        return place
    headers = {'accept': 'application/json'}
    token = os.getenv('API_WEATHER_KEY', '')
    url = nearest_place_api.replace('{lat}', lat).replace('{lon}', lon).replace('{key}', token)
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise WeatherError('get_place', f'(2) Bad response status code: {resp.status_code}')
    ret = json.loads(resp.content)
    place = Place.objects.create(
        place_id = ret['place_id'],
        name = ret['name'],
        adm_area1 = ret['adm_area1'],
        adm_area2 = ret['adm_area2'],
        country = ret['country'],
        lat = ret['lat'],
        lon = ret['lon'],
        timezone = ret['timezone'],
        type = ret['type'],
        search_name = '',
        lat_cut = lat_cut,
        lon_cut = lon_cut,
    )
    return place

def get_datetime_value(data: dict, field_name: str, timezone: str) -> datetime:
    value = data['results'][field_name]
    if '+' in value:
        tz_part = value.split('+')[1]
        if tz_part != '00:00':
            raise WeatherError('get_datetime_value', 'Expected datetime value with timezone 00:00. Got: ' + value)
        utc = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        to_zone = tz.gettz(timezone)
        local = utc.astimezone(to_zone)
        s_local = local.strftime('%Y-%m-%dT%H:%M:%S')
        ret = datetime.strptime(s_local, '%Y-%m-%dT%H:%M:%S')
        return ret
    ret = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    return ret


def get_astro(place: Place) -> AstroData:
    date = datetime.now().date()
    if AstroData.objects.filter(place=place.id, date=date).exists():
        astro = AstroData.objects.filter(place=place.id, date=date).get()
        return astro
    headers = {'accept': 'application/json'}
    url = astro_api.replace('{lat}', place.lat).replace('{lon}', place.lon).replace('{formatted}', '0')
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise WeatherError('get_astro', f'(2) Bad response status code: {resp.status_code}')
    ret = json.loads(resp.content)
    if ret['status'] != 'OK':
        raise WeatherError('get_astro', f'(2) Bad status in API data: {ret}')

    sunrise = get_datetime_value(ret, 'sunrise', place.timezone)
    sunset = get_datetime_value(ret, 'sunset', place.timezone)
    solar_noon = get_datetime_value(ret, 'solar_noon', place.timezone)
    civil_twilight_begin = get_datetime_value(ret, 'civil_twilight_begin', place.timezone)
    civil_twilight_end = get_datetime_value(ret, 'civil_twilight_end', place.timezone)
    nautical_twilight_begin = get_datetime_value(ret, 'nautical_twilight_begin', place.timezone)
    nautical_twilight_end = get_datetime_value(ret, 'nautical_twilight_end', place.timezone)
    astronomical_twilight_begin = get_datetime_value(ret, 'astronomical_twilight_begin', place.timezone)
    astronomical_twilight_end = get_datetime_value(ret, 'astronomical_twilight_end', place.timezone)

    astro = AstroData.objects.create(
        place = place,
        date = date,
        day_length = ret['results']['day_length'],
        sunrise = sunrise,
        sunset = sunset,
        solar_noon = solar_noon,
        civil_twilight_begin = civil_twilight_begin,
        civil_twilight_end = civil_twilight_end,
        nautical_twilight_begin = nautical_twilight_begin,
        nautical_twilight_end = nautical_twilight_end,
        astronomical_twilight_begin = astronomical_twilight_begin,
        astronomical_twilight_end = astronomical_twilight_end,
    )
    return astro

def get_forecast_api_data(place: Place) -> None:
    headers = {'accept': 'application/json'}
    token = os.getenv('API_WEATHER_KEY', '')
    timezone = os.getenv('API_WEATHER_TZ', '')
    url = forecast_api.replace('{place_id}', place.place_id).replace('{timezone}', timezone).replace('{key}', token)
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise WeatherError('get_forecast_api_data', f'Bad response status code: {resp.status_code}')
    ret = json.loads(resp.content)
    fixed = datetime.now().replace(second=0, microsecond=0)
    weather = Forecast.objects.create(
        place=place,
        event=fixed,
        fixed=fixed,
        ev_type=CURRENT,
        lat=ret['lat'],
        lon=ret['lon'],
        elevation=ret['elevation'],
        timezone=ret['timezone'],
        units=ret['units'],
        weather=ret['current']['icon'],
        icon=ret['current']['icon_num'],
        summary=ret['current']['summary'],
        temperature=ret['current']['temperature'],
        wind_speed=ret['current']['wind']['speed'],
        wind_angle=ret['current']['wind']['angle'],
        wind_dir=ret['current']['wind']['dir'],
        prec_total=ret['current']['precipitation']['total'],
        prec_type=ret['current']['precipitation']['type'],
        cloud_cover=ret['current']['cloud_cover'],
    )
    for hour in ret['hourly']['data']:
        Forecast.objects.create(
            place=place,
            event=datetime.strptime(hour['date'], '%Y-%m-%dT%H:%M:%S'),
            fixed=fixed,
            ev_type=FORECASTED_HOURLY,
            lat=ret['lat'],
            lon=ret['lon'],
            elevation=weather.elevation,
            timezone=weather.timezone,
            units=weather.units,
            weather=hour['weather'],
            icon=hour['icon'],
            summary=hour['summary'],
            temperature=hour['temperature'],
            temperature_min=None,
            temperature_max=None,
            wind_speed=hour['wind']['speed'],
            wind_angle=hour['wind']['angle'],
            wind_dir=hour['wind']['dir'],
            prec_total=hour['precipitation']['total'],
            prec_type=hour['precipitation']['type'],
            cloud_cover=hour['cloud_cover']['total'],
        )

    for day in ret['daily']['data']:
        Forecast.objects.create(
            place=place,
            event=datetime.strptime(day['day'], '%Y-%m-%d'),
            fixed=fixed,
            ev_type=FORECASTED_DAILY,
            lat=ret['lat'],
            lon=ret['lon'],
            elevation=weather.elevation,
            timezone=weather.timezone,
            units=weather.units,
            weather=day['weather'],
            icon=day['icon'],
            summary=day['summary'],
            temperature=day['all_day']['temperature'],
            temperature_min=day['all_day']['temperature_min'],
            temperature_max=day['all_day']['temperature_max'],
            wind_speed=day['all_day']['wind']['speed'],
            wind_angle=day['all_day']['wind']['angle'],
            wind_dir=day['all_day']['wind']['dir'],
            prec_total=day['all_day']['precipitation']['total'],
            prec_type=day['all_day']['precipitation']['type'],
            cloud_cover=day['all_day']['cloud_cover']['total'],
        )

@dataclass
class DayWeather:
    event: datetime
    state: str
    summary: str
    icon_num: int
    temperature: Decimal
    temperature_min: Decimal | None
    temperature_max: Decimal | None
    wind_speed: Decimal
    wind_dir: str
    wind_angle: int
    cloud_cover: int
    prec_total: Decimal
    prec_type: str

    def to_json(self):
        return {
            "event": self.event.strftime('%Y-%m-%dT%H:%M:%S'),
            "state": self.state,
            "summary": self.summary,
            "icon_num": self.icon_num,
            "temperature": '{0:.1f}'.format(self.temperature),
            "temperature_min": '{0:.1f}'.format(self.temperature_min) if self.temperature_min else None,
            "temperature_max": '{0:.1f}'.format(self.temperature_max) if self.temperature_max else None,
            "wind_speed": '{0:.1f}'.format(self.wind_speed),
            "wind_dir": self.wind_dir,
            "wind_angle": self.wind_angle,
            "cloud_cover": self.cloud_cover,
            "prec_total": '{0:.1f}'.format(self.prec_total),
            "prec_type": self.prec_type,
        }

@dataclass
class PeriodWeather:
    lat: str
    lon: str
    place: str
    elevation: int
    timezone: str
    units: str
    cr_url: str
    cr_info: str
    sunrise: datetime
    sunset: datetime
    current: DayWeather
    for_day: list[DayWeather] = field(default_factory=list)
    for_week: list[DayWeather] = field(default_factory=list)

    def to_json(self):
        return {
            "lat": self.lat,
            "lon": self.lon,
            "place": self.place,
            "elevation": self.elevation,
            "timezone": self.timezone,
            "units": self.units,
            "cr_url": self.cr_url,
            "cr_info": self.cr_info,
            "sunrise": self.sunrise.strftime('%Y-%m-%d %H:%M'),
            "sunset": self.sunset.strftime('%Y-%m-%d %H:%M'),
            "current": self.current.to_json(),
            "for_day": [x.to_json() for x in self.for_day],
            "for_week": [x.to_json() for x in self.for_week],
        }

def get_forecast_data(place: Place, forecast, astro: AstroData) -> dict:
    currents = forecast.filter(ev_type=CURRENT)
    if not len(currents):
        raise WeatherError('get_forecast_data', 'Empty forecast Queryset.')
    if not astro.sunrise or not astro.sunset:
        raise WeatherError('get_forecast_data', 'Empty AstroData values.')
    current = DayWeather(
        event=currents[0].event,
        state=currents[0].weather,
        summary=currents[0].summary,
        icon_num=currents[0].icon,
        temperature=currents[0].temperature,
        temperature_min=currents[0].temperature_min,
        temperature_max=currents[0].temperature_max,
        wind_speed=currents[0].wind_speed,
        wind_dir=currents[0].wind_dir,
        wind_angle=currents[0].wind_angle,
        cloud_cover=currents[0].cloud_cover,
        prec_total=currents[0].prec_total,
        prec_type=currents[0].prec_type,
    )
    data = PeriodWeather(
        lat=currents[0].lat,
        lon=currents[0].lon,
        place=place.name,
        sunrise=astro.sunrise,
        sunset=astro.sunset,
        elevation=currents[0].elevation,
        timezone=currents[0].timezone,
        units=currents[0].units,
        cr_url=os.getenv('API_WEATHER_CR_URL', '#'),
        cr_info=os.getenv('API_WEATHER_INFO', '#'),
        current=current,
    )
    for_day = forecast.filter(ev_type=FORECASTED_HOURLY)
    for x in for_day:
            data.for_day.append(DayWeather(
                event=x.event,
                state=x.weather,
                summary=x.summary,
                icon_num=x.icon,
                temperature=x.temperature,
                temperature_min=x.temperature_min,
                temperature_max=x.temperature_max,
                wind_speed=x.wind_speed,
                wind_dir=x.wind_dir,
                wind_angle=x.wind_angle,
                cloud_cover=x.cloud_cover,
                prec_total=x.prec_total,
                prec_type=x.prec_type,
            ))
    for_week = forecast.filter(ev_type=FORECASTED_DAILY)
    for x in for_week:
            data.for_week.append(DayWeather(
                event=x.event,
                state=x.weather,
                summary=x.summary,
                icon_num=x.icon,
                temperature=x.temperature,
                temperature_min=x.temperature_min,
                temperature_max=x.temperature_max,
                wind_speed=x.wind_speed,
                wind_dir=x.wind_dir,
                wind_angle=x.wind_angle,
                cloud_cover=x.cloud_cover,
                prec_total=x.prec_total,
                prec_type=x.prec_type,
            ))
    ret = data.to_json()
    return ret

def get_db_chart_data(user, location: str, lat: str, lon: str) -> dict:
    place = get_place(location, lat, lon)
    lifetime = datetime.now() - timedelta(hours=2)
    forecast = Forecast.objects.filter(place=place.id, fixed__gt=lifetime).order_by('event')
    astro = get_astro(place)
    if not len(forecast):
        get_forecast_api_data(place)
        forecast = Forecast.objects.filter(place=place.id, fixed__gt=lifetime).order_by('event')
    ret = get_forecast_data(place, forecast, astro)
    return ret

def get_chart_data(user, location: str, lat: str, lon: str):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_chart_data(location, lat, lon)
        return ret
    try:
        ret = get_db_chart_data(user, location, lat, lon)
        return {'result': 'ok', 'data': ret}
    except WeatherError as inst:
        proc, info = inst.args
        return {'result': 'error', 'procedure': proc, 'info': info}
