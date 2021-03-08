from django.db.models import Q
from hier.search import SearchResult
from hier.grp_lst import search as hier_search
from hier.params import get_search_mode
from .models import app_name, Task

def search(user, query):
    result = SearchResult(query)

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(url__icontains=query)
    elif (search_mode == 2):
        lookups = Q(categories__icontains=query[1:])
    
    items = Task.objects.filter(user = user.id).filter(lookups).distinct()
    for item in items:
        result.add(app_name, 'task', item.id, item.name, item.info)
    result.items += hier_search(user, app_name, query)
    return result.items
