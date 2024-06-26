from PIL import Image
from task.models import Task
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse, HttpResponseNotFound

def get_app_doc(request, role, pk, fname):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    path = task.get_attach_path(role)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()

def get_app_thumbnail(request, role, pk, fname) -> HttpResponse:
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    path = task.get_attach_path(role)
    img = Image.open(path + fname)
    img.thumbnail((36,36,))
    format = fname.split('.')[-1:][0].replace('jpg', 'jpeg')
    response = HttpResponse(content_type='image/' + format)
    img.save(response, format)
    return response
