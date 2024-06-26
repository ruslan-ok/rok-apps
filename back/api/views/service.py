import os
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

def scan_dir(root_dir):
    ret = []
    for dirname, subdirs, files in os.walk(root_dir):
        dirname = dirname.replace(root_dir, '')
        if dirname:
            dirname = dirname.replace('\\', '/')
        if dirname.startswith('/'):
            dirname = dirname[1:]
        fpath = os.path.join(root_dir, dirname).replace('\\', '/')
        for filename in files:
            if filename == 'Thumbs.db':
                continue
            fullname = os.path.join(fpath, filename).replace('\\', '/')
            mt = os.path.getmtime(fullname)
            dttm = datetime.fromtimestamp(mt)
            dttm = datetime.strptime(dttm.strftime('%m-%d-%Y %I:%M%p'), '%m-%d-%Y %I:%M%p')
            sz = os.path.getsize(fullname)
            x = {
                'status': 0,
                'folder': dirname,
                'name': filename,
                'date_time': dttm,
                'size': sz,
            }
            ret.append(x)
    return ret


@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def get_dir(request):
    if 'dir_role' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'dir_role'"},
                        status=HTTP_400_BAD_REQUEST)
    dir_role = request.query_params['dir_role']
    if dir_role not in ('backup', 'docs'):
        return Response({'Error': "The 'dir_role' parameter must have one of the following values: 'backup', 'docs'"},
                        status=HTTP_400_BAD_REQUEST)
    match dir_role:
        case 'backup': root_dir = settings.DJANGO_BACKUP_FOLDER
        case 'docs': root_dir = settings.DJANGO_STORAGE_PATH.replace('\\{}\\', '')
        case _: root_dir = 'k:/unknown'
    dirs = scan_dir(root_dir)
    data = {'dirs': dirs}
    return Response(data)
