from django.db.models import Q
from hier.search import SearchResult
from hier.grp_lst import search as hier_search
from .models import app_name, Task

def search(user, query):
    result = SearchResult(query)
    lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(url__icontains=query) | Q(categories__icontains=query)
    items = Task.objects.filter(user = user.id).filter(lookups).distinct()
    for item in items:
        result.add(app_name, 'task', item.id, item.name, item.info)
    result.items += hier_search(user, app_name, query)
    return result.items
