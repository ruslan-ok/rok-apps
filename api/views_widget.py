from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from todo.hp_widget import get_todo
from logs.hp_widget import get_logs
from health.views.chart import get_chart_data as get_health_data
from rusel.hp_widget import get_weather, get_visited, get_crypto, get_currency

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([TemplateHTMLRenderer])
def get_widget(request):
    id = request.GET.get('id', '???')
    context = {'widget_id': id}
    template_name = None
    match id:
        case 'todo': template_name, context = get_todo(request)
        case 'logs': template_name, context = get_logs(request)
        case 'weather': template_name, context = get_weather()
        case 'visited': template_name, context = get_visited(request)
        case 'crypto': template_name, context = get_crypto()
        case 'currency': template_name, context = get_currency()
        case 'health': template_name, context = 'widgets/health.html', {}
    if not template_name:
        template_name = 'widgets/fail.html'
    return Response(context, template_name=template_name)

ALL_CHART_MARKS = [
    'weight',
    'weight_last',
    'waist',
    'temp',
]

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_chart_data(request):
    if 'mark' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'mark'"},
                        status=HTTP_400_BAD_REQUEST)
    mark = request.query_params['mark']
    if mark not in ALL_CHART_MARKS:
        return Response({'Error': "The 'mark' parameter must have one of the following values: " + ', '.join(ALL_CHART_MARKS)},
                        status=HTTP_400_BAD_REQUEST)
    data = get_health_data(request.user.id, mark)
    return Response(data)
