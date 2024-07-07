import json, requests
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from core.currency.utils import get_exchange_rate_for_api


RATE_APIS = ('ecb', 'nbp', 'nbrb', 'boe', 'er', 'ca')
CURRENCIES = ('usd', 'eur', 'pln', 'byn', 'gbp')


def get_api_exchange_rate(request):
    api_url = settings.DJANGO_HOST_LOG
    service_token = settings.DJANGO_SERVICE_TOKEN
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = settings.DJANGO_CERT
    params = '&'.join([k + '=' + v for k, v in request.query_params.items()])
    url = api_url + '/api/core/get_exchange_rate/?' + params
    resp = requests.get(url, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return {'rate': None, 'num_units': None, 'url': url, 'info': "Response status code: " + str(resp.status_code)}
    return json.loads(resp.content)

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_exchange_rate(request):

    if settings.DJANGO_DEVICE != settings.DJANGO_LOG_DEVICE:
        ret = get_api_exchange_rate(request)
        return Response(ret)

    if 'date' not in request.query_params:
        return Response({'rate': None, 'num_units': None, 'info': "Expected parameter 'date'"}, status=HTTP_400_BAD_REQUEST)
    rate_date_str = request.query_params['date']
    try:
        rate_date = datetime.strptime(rate_date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'rate': None, 'num_units': None, 'info': "The 'rate_date' parameter must be in format 'YYYY-MM-DD'."}, status=HTTP_400_BAD_REQUEST)

    if 'currency' not in request.query_params:
        return Response({'rate': None, 'num_units': None, 'info': "Expected parameter 'currency'"}, status=HTTP_400_BAD_REQUEST)
    currency = request.query_params['currency'].lower()
    if currency not in CURRENCIES:
        return Response({'rate': None, 'num_units': None, 'info': "The 'currency' parameter must have one of the following values: " + ', '.join(CURRENCIES)}, status=HTTP_400_BAD_REQUEST)

    base = request.query_params.get('base', 'USD').lower()
    if base not in CURRENCIES:
        return Response({'rate': None, 'num_units': None, 'info': "The 'base' parameter must have one of the following values: " + ', '.join(CURRENCIES)}, status=HTTP_400_BAD_REQUEST)

    rate_api = request.query_params.get('rate_api', None)
    if rate_api and rate_api not in RATE_APIS:
        return Response({'rate': None, 'num_units': None, 'info': "The 'rate_api' parameter must have one of the following values: " + ', '.join(RATE_APIS)}, status=HTTP_400_BAD_REQUEST)

    mode = request.query_params.get('mode', 'can_update')

    currency_rate, info = get_exchange_rate_for_api(rate_date, currency, base, rate_api, mode)
    rate = num_units = None
    if currency_rate:
        if type(currency_rate) == Decimal:
            rate = currency_rate
            num_units = 1
        else:    
            rate = currency_rate.value
            num_units = currency_rate.num_units
    return Response({'rate': rate, 'num_units': num_units, 'info': info})
