from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from todo.hp_widget import get_todo
from rusel.hp_widget import get_logs, get_weather, get_visited, get_crypto, get_currency, get_health

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([TemplateHTMLRenderer])
def get_widget(request):
    id = request.GET.get('id', '???')
    context = {'widget_id': id}
    template_name = None
    match id:
        case 'todo': template_name, context = get_todo(request)
        case 'logs': template_name, context = get_logs()
        case 'weather': template_name, context = get_weather()
        case 'visited': template_name, context = get_visited()
        case 'crypto': template_name, context = get_crypto()
        case 'currency': template_name, context = get_currency()
        case 'health': template_name, context = get_health()
    if not template_name:
        template_name = 'widgets/fail.html'
    resp = Response(context, template_name=template_name)
    return resp
