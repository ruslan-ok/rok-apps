from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from core.context import Context
from task.const import APP_TODO


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def fixed(request):
    context = Context()
    context.request = request
    context.set_config(APP_TODO)
    context.config.set_view(request)
    fixes = context.get_fixes(context.config.views, search_qty=None)
    return Response(fixes)
