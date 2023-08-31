import os
from datetime import datetime, date
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST
from todo.hp_widget.todo import get_todo
from logs.hp_widget.logs import get_logs
from core.hp_widget.visited import get_visited
from health.views.chart import get_chart_data as get_health_data
from core.hp_widget.currency import get_currency, get_chart_data as get_currency_data
from core.hp_widget.crypto import get_crypto, get_chart_data as get_crypto_data
from core.hp_widget.weather import get_weather, get_chart_data as get_weather_data
from weather.utils import get_chart_data as get_forecast
from core.hp_widget.delta import ChartPeriod, ChartDataVersion

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([TemplateHTMLRenderer])
def get_widget(request):
    id = request.GET.get('id', '???')
    context = {'widget_id': id}
    template_name = None
    match id:
        case 'todo': template_name, context = get_todo(request)
        case 'logs': template_name, context = get_logs(request)
        case 'weather': template_name, context = get_weather(request)
        case 'visited': template_name, context = get_visited(request)
        case 'crypto': template_name, context = get_crypto(request)
        case 'currency': template_name, context = get_currency(request)
        case 'health': template_name, context = 'hp_widget/health.html', {}
    if not template_name:
        template_name = 'widgets/fail.html'
    elif template_name == 'hide':
        return HttpResponse('')
    return Response(context, template_name=template_name)

ALL_CHART_MARKS = [
    'weight',
    'waist',
    'temp',
    'health',
    'currency',
    'crypto',
    'weather',
]

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_chart_data(request):
    if 'mark' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'mark'"},
                        status=HTTP_400_BAD_REQUEST)
    mark = request.query_params['mark']
    if mark not in ALL_CHART_MARKS:
        return Response({'Error': "The 'mark' parameter must have one of the following values: " + ', '.join(ALL_CHART_MARKS)},
                        status=HTTP_400_BAD_REQUEST)
    s_period = request.GET.get('period', '')
    s_version = request.GET.get('version', '1')
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
    try:
        version = ChartDataVersion(s_version)
    except:
        version = ChartDataVersion.v1

    match mark:
        case 'weight' | 'waist' | 'temp' | 'health': data = get_health_data(request.user.id, mark, period, version)
        case 'currency': data = get_currency_data(request.user.id, period, version, base)
        case 'crypto': data = get_crypto_data(period, version)
        case 'weather':
            match version:
                case ChartDataVersion.v1: data = get_weather_data(request.user.id)
                case ChartDataVersion.v2: data = get_forecast(request.user, location, lat, lon)
                case _: data = {}
        case _: data = {}
    return Response(data)

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_hist_exchange_rates(request):
    currency = request.GET.get('currency', '')
    s_beg = request.GET.get('beg', '')
    s_end = request.GET.get('end', '')
    if not currency or not s_beg or not s_end:
        return Response({'result': 'error', 'error': "Expected parameters 'currency', 'beg' and 'end'"},
                        status=HTTP_400_BAD_REQUEST)
    try:
        d_beg: date = datetime.strptime(s_beg, '%Y-%m-%d').date()
    except:
        return Response({'result': 'error', 'error': "Expected parameter 'beg' as date in format 'YYYY-MM-DD'"},
                        status=HTTP_400_BAD_REQUEST)
    try:
        d_end: date = datetime.strptime(s_end, '%Y-%m-%d').date()
    except:
        return Response({'result': 'error', 'error': "Expected parameter 'end' as date in format 'YYYY-MM-DD'"},
                        status=HTTP_400_BAD_REQUEST)

    data = get_db_hist_exchange_rates(currency, d_beg, d_end)
    return Response(data)
