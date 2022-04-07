from task.models import Task
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseNotFound

def get_app_doc(app, role, request, pk, fname):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    path = task.get_attach_path(app, role)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()
