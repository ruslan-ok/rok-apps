import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def apps(request):
    data = [
        {
            "name": "app-1",
            "icon": "icon-1",
        },
        {
            "name": "app-2",
            "icon": "icon-2",
        },
    ]
    json_data = json.dumps(data)
    return Response(json_data)
