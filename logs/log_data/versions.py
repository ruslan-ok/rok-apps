import os, datetime, django, rest_framework, OpenSSL, ssl, urllib.request
from platform import python_version
from rusel.mysql_ver import get_mysql_ver
from logs.log_data.log_data import LogData

class VersionsLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['python_version'] = python_version()
        context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
        context['drf_version'] = '{}'.format(rest_framework.VERSION)
        context['weather_api_key'] = os.environ.get('OPENWEATHER_API_KEY')
        context['weather_city_id'] = os.environ.get('OPENWEATHER_CITY_ID')
        host = os.environ.get('DJANGO_HOST')
        api_host = os.environ.get('DJANGO_HOST_API')
        if host != 'localhost':
            response = urllib.request.urlopen(api_host)
            versions = response.headers['Server'].split(' ')
            for ver in versions:
                if 'Apache' in ver:
                    context['apache_version'] = ver.split('/')[1]
                if 'OpenSSL' in ver:
                    context['openssl_version'] = ver.split('/')[1]
                if 'mod_wsgi' in ver:
                    context['mod_wsgi_version'] = ver.split('/')[1]
        context['hmail_version'] = '5.6.7 bld 2425'
        context['mysql_version'] = get_mysql_ver()
        context['leaflet_version'] = get_leaflet_ver()
        context['bootstrap_version'] = get_bootstrap_ver()
        context['izitoast_version'] = get_izitoast_ver()
        context['chartjs_version'] = get_chartjs_ver()
        context['swiper_version'] = get_swiper_ver()
        context['firebase_version'] = get_firebase_ver()

        try:
            cert = ssl.get_server_certificate(('rusel.by', 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            t = x509.get_notAfter()
            d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
            context['cert_termin'] = d.strftime('%d.%m.%Y')
        except:
            pass
        return context


def get_leaflet_ver():
    return '1.7.1'

def get_bootstrap_ver():
    return '5.1.0'

def get_izitoast_ver():
    return '1.4.0'

def get_chartjs_ver():
    return '3.7.0'

def get_swiper_ver():
    return '8.0.7'

def get_firebase_ver():
    return '5.2.0'

