from django.db.models import Q
from hier.search import SearchResult
from .models import app_name, Projects, Expenses

def search(user, query):
    result = SearchResult(query)
    
    lookups = Q(name__icontains=query)
    items = Projects.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, 'project', item.id, item.name, item.get_summary(), False)

    lookups = Q(kontr__icontains=query) | Q(text__icontains=query) | Q(description__icontains=query)
    items = Expenses.objects.filter(direct__user = user.id).filter(lookups)
    for item in items:
        info = item.kontr
        if info and item.text:
            info += ', '
        info += item.text
        result.add(app_name, 'expense', item.id, item.name(), info, True, item.direct.name)

    return result.items
