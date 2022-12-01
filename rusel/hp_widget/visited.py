from task.models import VisitedHistory
from rusel.context import MAX_LAST_VISITED

def get_visited(request):
    last_visited = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]
    context = {'last_visited': last_visited}
    template_name = 'hp_widget/visited.html'
    return template_name, context
