import requests, json, os
from datetime import datetime, timedelta
from task.models import Weather, CURRENT, FORECASTED_DAILY

def get_weather(request):
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
                weather = Weather.objects.create(
                    event=datetime.now(),
                    fixed=datetime.now(),
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
                for day in ret['daily']['data']:
                    Weather.objects.create(
                        event=datetime.strptime(day['day'], '%Y-%m-%d'),
                        fixed=datetime.now(),
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
