"""Collecting statistics of site visits."""
import collections
from datetime import datetime
from functools import reduce
from django.utils.translation import gettext_lazy as _
from .models import IPInfo, AccessLog, SiteStat
from hier.utils import APPS

def get_site_stat(user):
    """Processing a new portion of log file records.

    The site applications that users have visited and information about their IP addresses will be shown.
    """
    TOTAL_IP = _('total different').capitalize() + ' IP'
    TOTAL_LOG = _('total log records').capitalize()
    NEW_LOG = _('new log records').capitalize()

    cnt = collections.Counter()
    cnt[TOTAL_IP] = len(IPInfo.objects.all())
    cnt[TOTAL_LOG] = len(AccessLog.objects.all())

    #Determining the last previously processed log file entry
    last = datetime.min
    site_stat = None
    if SiteStat.objects.filter(user=user.id).exists():
        site_stat = SiteStat.objects.filter(user = user.id).get()
        if site_stat.record and site_stat.record.event:
            last = site_stat.record.event

    # New records
    records = AccessLog.objects.filter(event__gt=last).order_by('-event')
    cnt[NEW_LOG] += len(records)

    # Save last processed log record
    last_rec = None
    if (len(records) > 0):
        last_rec = records[0]
        if site_stat:
            site_stat.record = last_rec
            site_stat.save()
        else:
            SiteStat.objects.create(user=user, record=last_rec)

    #raise Exception(last_rec.event)
    apps = {}
    for rec in records:
        uri = valid_uri(rec)
        if not uri:
            continue

        # Determining the access to the site application
        a_app = list(filter(lambda x: '/{}/'.format(x) in uri, APPS))
        if not a_app:
            continue
                    
        app = a_app[0]
        if not app in apps:
            apps[app] = {}        
        host = str(rec.host.info())
        #raise Exception('aaa = ', aaa)
        if not host in apps[app]:
            apps[app][host] = []
            
        page = '{} {}'.format(rec.method, uri)
        if not page in apps[app][host]:
            apps[app][host].append(page)

    return cnt.most_common(), apps

def valid_uri(rec):
    if (rec.status >= 400) or (rec.status == 301):
        return None
    if 'favicon.ico' in rec.uri or '/static/' in rec.uri or '/jsi18n/' in rec.uri or '/photo/get_mini/' in rec.uri:
        return None
    if ('/?' in rec.uri) and (rec.method != 'POST'):
        uri = rec.uri.split('?')[0]
    else:
        uri = rec.uri
    uri = uri.replace('/ru/', '/').replace('/en/', '/')
    if (uri == '/'):
        return None
    return uri
    

