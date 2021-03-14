from django.db.models import Q
from hier.search import SearchResult
from .models import app_name, Apart, Meter, Bill, Service, Price

def search(user, query):
    result = SearchResult(query)
    
    lookups = Q(name__icontains=query) | Q(addr__icontains=query)
    items = Apart.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'apart', item.id, None, item.name, item.addr, False)

    lookups = Q(info__icontains=query)
    items = Meter.objects.filter(apart__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'meter', item.id, item.reading.date(), item.name(), item.info, False, item.apart.name, item.period.strftime('%m.%Y'))

    lookups = Q(info__icontains=query) | Q(url__icontains=query)
    items = Bill.objects.filter(apart__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'bill', item.id, item.payment.date(), item.name(), item.info, False, item.apart.name, item.period.strftime('%m.%Y'))

    lookups = Q(name__icontains=query) | Q(abbr__icontains=query)
    items = Service.objects.filter(apart__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'service', item.id, None, item.name, item.abbr, False, item.apart.name)

    lookups = Q(info__icontains=query)
    items = Price.objects.filter(apart__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'price', item.id, item.start, item.name(), item.info, False, item.apart.name)

    return result.items
