from django.db.models import Q
from hier.search import SearchResult
from hier.grp_lst import search as hier_search
from .models import app_name, Entry

def search(user, query):
    result = SearchResult(query)
    lookups = Q(title__icontains=query) | Q(username__icontains=query) | Q(url__icontains=query) | Q(notes__icontains=query) | Q(value__icontains=query) | Q(categories__icontains=query)
    items = Entry.objects.filter(user = user.id).filter(lookups).distinct()
    for item in items:
        info = ''
        if query in item.value:
            info = '[Value = "********"]'
            if item.notes:
                info += ', '
        if item.notes:
            info += item.notes
        result.add(app_name, 'entry', item.id, item.title, info)
    result.items += hier_search(user, app_name, query)
    return result.items
