import os
from datetime import datetime, date
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from todo.hp_widget.todo import get_todo
from core.hp_widget.visited import get_visited
from health.views.chart import get_health_data
from core.hp_widget.currency import get_currency_data
from core.hp_widget.crypto import get_crypto_data
from weather.utils import get_forecast
from core.hp_widget.delta import ChartPeriod

ALL_CHART_MARKS = [
    'weight',
    'waist',
    'temp',
    'health',
    'currency',
    'crypto',
    'weather',
    'visited',
    'todo',
]

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_chart_data_api(request):
    if 'mark' not in request.query_params:
        return Response({'result': 'error', 'info': "Expected parameter 'mark'"},
                        status=HTTP_400_BAD_REQUEST)
    mark = request.query_params['mark']
    if mark not in ALL_CHART_MARKS:
        return Response({'result': 'error', 'info': "The 'mark' parameter must have one of the following values: " + ', '.join(ALL_CHART_MARKS)},
                        status=HTTP_400_BAD_REQUEST)
    filter = request.query_params.get('filter', None)
    s_period = request.GET.get('period', '')
    base = request.GET.get('base', 'usd')
    location = request.GET.get('location', '')
    lat = request.GET.get('lat', os.getenv('API_WEATHER_LAT'))
    lon = request.GET.get('lon', os.getenv('API_WEATHER_LON'))
    try:
        period = ChartPeriod(s_period)
    except:
        match mark:
            case 'weight' | 'waist' | 'temp': period = ChartPeriod.p10y
            case 'health': period = ChartPeriod.p30d
            case 'currency': period = ChartPeriod.p7d
            case 'crypto': period = ChartPeriod.p7d
            case 'weather': period = ChartPeriod.p7d
            case _: period = ChartPeriod.p30d

    match mark:
        case 'weight' | 'waist' | 'temp' | 'health': data = get_health_data(request.user.id, mark, period, filter)
        case 'currency': data = get_currency_data(period, base)
        case 'crypto': data = get_crypto_data(period)
        case 'visited': data = get_visited(request)
        case 'todo': data = get_todo(request)
        case 'weather': data = get_forecast(request.user, location, lat, lon)
        case _: data = {'result': 'error', 'info': 'Unknown widget: ' + mark}
    return Response(data)
