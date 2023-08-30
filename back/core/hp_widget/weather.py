import requests, json, os, time
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
from task.models import Weather, CURRENT, FORECASTED_DAILY, FORECASTED_HOURLY
from core.hp_widget.delta import ChartDataVersion
from logs.models import ServiceTask

def get_weather():
    weather = None
    context = {}
    lat = os.getenv('API_WEATHER_LAT')
    lon = os.getenv('API_WEATHER_LON')
    lifetime = datetime.now() - timedelta(hours=2)
    data = Weather.objects.filter(lat=lat, lon=lon, ev_type=CURRENT, event__gt=lifetime).order_by('-event')
    if len(data) > 0:
        weather = data[0]
    else:
        api_url = os.getenv('API_WEATHER')
        headers = {'accept': 'application/json'}
        token = os.getenv('API_WEATHER_KEY')
        timezone = os.getenv('API_WEATHER_TZ')
        if api_url and lat and lon and timezone and token:
            url = api_url.replace('{lat}', lat).replace('{lon}', lon).replace('{timezone}', timezone).replace('{token}', token)
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                ret = json.loads(resp.content)
                fixed = datetime.now().replace(second=0, microsecond=0)
                weather = Weather.objects.create(
                    event=datetime.now(),
                    fixed=fixed,
                    ev_type=CURRENT,
                    lat=lat,
                    lon=lon,
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
                    Weather.objects.create(
                        event=datetime.strptime(hour['date'], '%Y-%m-%dT%H:%M:%S'),
                        fixed=fixed,
                        ev_type=FORECASTED_HOURLY,
                        lat=lat,
                        lon=lon,
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
                    Weather.objects.create(
                        event=datetime.strptime(day['day'], '%Y-%m-%d'),
                        fixed=fixed,
                        ev_type=FORECASTED_DAILY,
                        lat=lat,
                        lon=lon,
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
    api_url = os.getenv('API_WEATHER_CR_URL', '#')
    if weather:
        context['weather_url'] = os.getenv('API_WEATHER_INFO', '#')
        context['temp_value'] = weather.temperature
        context['summary'] = weather.summary
        context['current_weather_icon'] = api_url + f'/static/img/ico/weather/{weather.icon}.svg'
    context['copyright_url'] = api_url
    context['copyright_info'] = os.getenv('API_WEATHER_CR_INFO', '')
    template_name = 'hp_widget/weather.html'
    return template_name, context

# Prevent double run from React StrictMode
def service_available(user) -> bool:
    lifetime = datetime.now() - timedelta(minutes=1)
    ServiceTask.objects.filter(user=user.id, app='weather', service='widget', created__lt=lifetime).delete()
    tasks = ServiceTask.objects.filter(user=user.id, app='weather', service='widget', created__gt=lifetime)
    if len(tasks):
        stop = datetime.now() + timedelta(minutes=1)
        while datetime.now() < stop:
            tasks = ServiceTask.objects.filter(user=user.id, app='weather', service='widget', created__gt=lifetime)
            if len(tasks) == 0:
                ServiceTask.objects.create(user=user, app='weather', service='widget')
                return True
            time.sleep(5)
        return False
    ServiceTask.objects.create(user=user, app='weather', service='widget')
    return True

def free_service(user):
    ServiceTask.objects.filter(user=user.id, app='weather', service='widget').delete()

def get_db_chart_data(user, version: ChartDataVersion, place: str):
    data = {}
    match version:
        case ChartDataVersion.v1:
            lat = 54.093709
            lon = 28.295668
            lifetime = datetime.now() - timedelta(hours=4, minutes=1)
            weather = Weather.objects.filter(lat=lat, lon=lon, ev_type=FORECASTED_DAILY, fixed__gt=lifetime).order_by('-fixed')
            data = get_weather_data_v1(weather)
        case ChartDataVersion.v2:
            if service_available(user):
                lifetime = datetime.now() - timedelta(hours=2)
                get_weather()
                lat = os.getenv('API_WEATHER_LAT')
                lon = os.getenv('API_WEATHER_LON')
                weather = Weather.objects.filter(lat=lat, lon=lon, fixed__gt=lifetime).order_by('event')
                data = get_weather_data_v2(weather)
                free_service(user)
    return data

def get_weather_data_v1(weather):
    x = []
    y = []
    for day in weather:
        if day.event:
            x.append(day.event.strftime('%m.%d'))
            y.append(day.temperature_min)
            x.append(day.event.strftime('%m.%d'))
            y.append(day.temperature_max)

    data = {
        'type': 'line',
        'data': {'labels': reversed(x),
            'datasets': [
                {
                    'label': 'Temperature minimum',
                    'data': reversed(y),
                    'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                    'borderColor': 'rgba(111, 184, 71, 1)',
                    'borderWidth': 1,
                    'tension': 0.4,
                },
            ]
        },
        'options': {
            'plugins': {
                'legend': {
                    'display': False,
                },
            },
            'elements': {
                'point': {
                    'radius': 0,
                },
            },
        },
    }
    return data

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
    place: str | None
    elevation: int
    timezone: str
    units: str
    cr_url: str
    cr_info: str
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
            "current": self.current.to_json(),
            "for_day": [x.to_json() for x in self.for_day],
            "for_week": [x.to_json() for x in self.for_week],
        }

def get_weather_data_v2(weather):
    currents = weather.filter(ev_type=CURRENT)
    if len(currents):
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
            place="Wrocław",
            elevation=currents[0].elevation,
            timezone=currents[0].timezone,
            units=currents[0].units,
            cr_url=os.getenv('API_WEATHER_CR_URL', '#'),
            cr_info=os.getenv('API_WEATHER_INFO', '#'),
            current=current,
        )
        for_day = weather.filter(ev_type=FORECASTED_HOURLY)
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
        for_week = weather.filter(ev_type=FORECASTED_DAILY)
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
    return {}

def get_api_chart_data(version: ChartDataVersion, place: str):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=weather&version=' + version.value + '&place=' + place, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def get_chart_data(user, version: ChartDataVersion, place: str):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_chart_data(version, place)
        if ret:
            print('-get_chart_data()')
            return ret
    return get_db_chart_data(user, version, place)

