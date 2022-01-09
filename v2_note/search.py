from django.db.models import Q
from v2_hier.search import SearchResult
from v2_hier.grp_lst import search as hier_search
from note.models import app_name, Note

def search(user, query):
    result = SearchResult(query)
    lookups = Q(name__icontains=query) | Q(code__icontains=query) | Q(descr__icontains=query) | Q(url__icontains=query) | Q(categories__icontains=query)
    items = Note.objects.filter(user = user.id, kind = 'note').filter(lookups).distinct()
    for item in items:
        result.add('note', 'note', item.id, item.publ.date(), item.name, item.descr)
    items = Note.objects.filter(user = user.id, kind = 'news').filter(lookups).distinct()
    for item in items:
        result.add('news', 'news', item.id, item.publ.date(), item.name, item.descr)
    result.items += hier_search(user, 'note', query)
    result.items += hier_search(user, 'news', query)
    return result.items
