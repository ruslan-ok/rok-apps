import os
from datetime import datetime
from django.conf import settings
from pathlib import Path
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from core.currency.utils import get_exchange_rate_for_api


def skip_file(name):
    return name == 'Thumbs.db' or name.startswith('~$') or name.startswith('.~lock.')

def scan_dir(root_dir: str, except_dir: str|None=None):
    ret = []
    if not root_dir:
        return ret
    for dirname, _, files in Path(root_dir).walk():
        if except_dir and dirname.is_relative_to(Path(except_dir)):
            continue
        for filename in files:
            if skip_file(filename):
                continue
            file = Path(dirname) / filename
            mt = file.stat().st_mtime
            dttm = datetime.fromtimestamp(mt)
            dttm = datetime.strptime(dttm.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            sz = file.stat().st_size
            x = {
                'status': 0,
                'folder': dirname.relative_to(Path(root_dir)).as_posix(),
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
    if 'folder' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'folder'"},
                        status=HTTP_400_BAD_REQUEST)
    folder = request.query_params['folder']
    file_list = scan_dir(folder)
    data = {'root_dir': folder, 'file_list': file_list}
    return Response(data)

# Modify the modification time of a file.
@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def modify_mt(request):
    if 'path' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'path'"},
                        status=HTTP_400_BAD_REQUEST)
    if 'mod_time' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'mod_time'"},
                        status=HTTP_400_BAD_REQUEST)
    path = request.query_params['path']
    mod_time_str = request.query_params['mod_time']
    mod_time = datetime.strptime(mod_time_str, '%Y-%m-%dT%H:%M:%S')
    dt_epoch = mod_time.timestamp()
    try:
        os.utime(path, (dt_epoch, dt_epoch))
        return Response({'result': 'ok'})
    except Exception as ex:
        ret = {'result': 'exception', 'exception': ex.strerror} # type: ignore
        return Response(ret)

@api_view()
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def exchange_rate_update(request):
    if 'currency' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'currency'"},
                        status=HTTP_400_BAD_REQUEST)
    if 'api_name' not in request.query_params:
        return Response({'result': 'error', 'error': "Expected parameter 'api_name'"},
                        status=HTTP_400_BAD_REQUEST)
    currency = request.query_params['currency']
    api_name = request.query_params['api_name']
    rate, info = get_exchange_rate_for_api(datetime.today().date(), currency, 'USD', api_name, mode='api_only_lad')
    return Response({'result': 'ok', 'info': info})
