import json
from health.views.chart import build_weight_chart

def get_health(request):
    data = build_weight_chart(request.user, compact=True)
    s_data = json.dumps(data)
    context = {'chart_data': s_data}
    template_name = 'widgets/health.html'
    return template_name, context
