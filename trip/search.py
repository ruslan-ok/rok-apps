from django.db.models import Q
from hier.search import SearchResult
from .models import app_name, Person, Trip

def search(user, query):
    result = SearchResult(query)
    
    lookups = Q(name__icontains=query) | Q(dative__icontains=query)
    items = Person.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'pers', item.id, item.name, item.dative, False)

    lookups = Q(text__icontains=query)
    items = Trip.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'trip', item.id, item.name(), item.text)

    return result.items
