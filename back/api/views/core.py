# import os
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from core.currency.utils import get_net_exchange_rate_for_api

# from todo.hp_widget.todo import get_todo
# from core.hp_widget.visited import get_visited
# from health.views.chart import get_health_data
# from core.hp_widget.currency import get_currency_data
# from core.hp_widget.crypto import get_crypto_data
# from weather.utils import get_forecast
# from core.hp_widget.delta import ChartPeriod

RATE_APIS = ('ecb', 'nbp', 'nbrb', 'er', 'ca')
CURRENCIES = ('usd', 'eur', 'pln', 'byn', 'gbp')


@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_net_exchange_rate(request):
    if 'rate_api' not in request.query_params:
        return Response({'result': 'error', 'info': "Expected parameter 'rate_api'"}, status=HTTP_400_BAD_REQUEST)
    rate_api = request.query_params['rate_api']
    if rate_api not in RATE_APIS:
        return Response({'result': 'error', 'info': "The 'rate_api' parameter must have one of the following values: " + ', '.join(RATE_APIS)}, status=HTTP_400_BAD_REQUEST)
    if 'base' not in request.query_params:
        return Response({'result': 'error', 'info': "Expected parameter 'base'"}, status=HTTP_400_BAD_REQUEST)
    base = request.query_params['base']
    if base not in CURRENCIES:
        return Response({'result': 'error', 'info': "The 'base' parameter must have one of the following values: " + ', '.join(CURRENCIES)}, status=HTTP_400_BAD_REQUEST)
    if 'currency' not in request.query_params:
        return Response({'result': 'error', 'info': "Expected parameter 'currency'"}, status=HTTP_400_BAD_REQUEST)
    currency = request.query_params['currency']
    if currency not in CURRENCIES:
        return Response({'result': 'error', 'info': "The 'currency' parameter must have one of the following values: " + ', '.join(CURRENCIES)}, status=HTTP_400_BAD_REQUEST)
    if 'rate_date' not in request.query_params:
        return Response({'result': 'error', 'info': "Expected parameter 'rate_date'"}, status=HTTP_400_BAD_REQUEST)
    rate_date_str = request.query_params['rate_date']
    try:
        rate_date = datetime.strptime(rate_date_str, '%Y-%m-%d').date()
    except Exception as ex:
        return Response({'result': 'error', 'info': "The 'rate_date' parameter must be in format 'YYYY-MM-DD'."}, status=HTTP_400_BAD_REQUEST)
    data = get_net_exchange_rate_for_api(rate_api, currency, rate_date, base)
    ret = data.to_json()
    return Response(ret)
