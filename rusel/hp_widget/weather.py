import requests, json, os
from datetime import datetime, timedelta
from task.models import Weather, CURRENT, FORECASTED_DAILY

def get_weather(request):
    weather = None
    context = {}
    lat = os.getenv('API_WEATHER_LAT')
    lon = os.getenv('API_WEATHER_LON')
    lifetime = datetime.now() - timedelta(hours=4)
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
    if weather:
        context['weather_url'] = os.getenv('API_WEATHER_INFO', '#')
        context['temp_value'] = weather.temperature
    template_name = 'hp_widget/weather.html'
    return template_name, context

def get_chart_data(user_id: int):
    x = []
    y_min = []
    y_max = []
    lat = 54.093709
    lon = 28.295668
    lifetime = datetime.now() - timedelta(hours=4, minutes=1)
    weather = Weather.objects.filter(lat=lat, lon=lon, ev_type=FORECASTED_DAILY, fixed__gt=lifetime).order_by('-fixed')
    for day in weather:
        if day.event:
            x.append(day.event.strftime('%m.%d'))
            y_min.append(day.temperature_min)
            y_max.append(day.temperature_max)

    data = {
        'type': 'line',
        'data': {'labels': reversed(x),
            'datasets': [
                {
                    'label': 'Temperature minimum',
                    'data': reversed(y_min),
                    'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                    'borderColor': 'rgba(111, 184, 71, 1)',
                    'borderWidth': 1,
                    'tension': 0.4,
                },
                {
                    'label': 'Temperature maximum',
                    'data': reversed(y_max),
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
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