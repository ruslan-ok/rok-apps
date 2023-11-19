from task.models import VisitedHistory
from rusel.context import MAX_LAST_VISITED

def get_visited(request):
    last_visited = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]
    context = {'last_visited': last_visited}
    template_name = 'hp_widget/visited.html'
    return template_name, context

def get_visited_v2(request):
    try:
        pinned = VisitedHistory.objects.filter(user=request.user.id, pinned=True).order_by('-stamp')
        visited = list(pinned)
        if len(pinned) < MAX_LAST_VISITED:
            last_visited = VisitedHistory.objects.filter(user=request.user.id, pinned=False).order_by('-stamp')[:MAX_LAST_VISITED-len(pinned)]
            visited += list(last_visited)
        data = [{
            'id': x.id, 
            'stamp': x.stamp, 
            'url': x.href, 
            'app': x.app, 
            'page': x.page, 
            'info': x.info, 
            'icon': 'bi-' + (x.icon if x.icon else 'question-square'), 
            'title': x.title(),
            'pinned': x.pinned,
        } for x in visited]
        ret = {'result': 'ok', 'data': data, 'title': 'Last visited pages'}
        return ret
    except Exception as ex:
        return {'result': 'error', 'info': 'Exception: ' + str(ex)}
