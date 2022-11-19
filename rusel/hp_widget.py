from task.models import VisitedHistory
from rusel.context import MAX_LAST_VISITED

def get_visited(request):
    last_visited = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]
    context = {'last_visited': last_visited}
    template_name = 'widgets/visited.html'
    return template_name, context

def get_crypto():
    context = {'widget_id': 'crypto'}
    template_name = None
    return template_name, context

def get_currency():
    context = {'widget_id': 'currency'}
    template_name = None
    return template_name, context

def get_weather():
    context = {'widget_id': 'weather'}
    template_name = None
    return template_name, context

