from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from core.context import DirContext
from core.dir_forms import UploadForm

#----------------------------------------------------------------------
class BaseDirView(DirContext, FormView):
    form_class = UploadForm

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app)

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        return ret

    def init_store_dir(self, user):
        self.store_dir = f'{settings.DJANGO_STORAGE_PATH}/{user.username}/docs'

    def post(self, request, *args, **kwargs):
        self.init_store_dir(request.user)
        folder = ''
        if ('folder' in request.GET):
            folder = request.GET['folder']
        if folder:
            folder += '/'
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('upload')
        if form.is_valid():
            for f in files:
                self.handle_uploaded_file(f, folder)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def handle_uploaded_file(self, f, folder):
        path = self.store_dir + folder
        with open(path + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
