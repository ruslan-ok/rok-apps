from django.db.models import Q
from hier.search import SearchResult
from .models import app_name, Car, Fuel, Part, Repl

def search(user, query):
    result = SearchResult(query)
    
    lookups = Q(name__icontains=query) | Q(plate__icontains=query)
    items = Car.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'cars', item.id, None, item.name, item.plate, False)

    lookups = Q(comment__icontains=query)
    items = Fuel.objects.filter(car__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'fuel', item.id, item.pub_date.date(), str(item), item.comment, True, item.car.name)

    lookups = Q(name__icontains=query) | Q(comment__icontains=query)
    items = Part.objects.filter(car__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'interval', item.id, None, item.name, item.info(), False, item.car.name)

    lookups = Q(manuf__icontains=query) | Q(part_num__icontains=query) | Q(descr__icontains=query) | Q(comment__icontains=query)
    items = Repl.objects.filter(car__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'service', item.id, item.dt_chg.date(), str(item), item.info(), False, item.car.name)

    return result.items
