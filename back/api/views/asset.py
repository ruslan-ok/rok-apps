import os
from django.http import FileResponse, HttpResponseNotFound
from rok.settings import STATICFILES_DIRS


def get_asset(request, file):
    try:
        static_path = STATICFILES_DIRS[0]
        folder = os.path.join(static_path, 'assets')
        filepath = folder + '\\' + file
        fsock = open(filepath, 'rb')
        response = FileResponse(fsock)
        return response
    except IOError:
        return HttpResponseNotFound()
