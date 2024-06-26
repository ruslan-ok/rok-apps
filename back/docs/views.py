import urllib.parse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import FileResponse, HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from core.dir_views import BaseDirView

role = 'doc'
app = 'docs'

class FolderView(LoginRequiredMixin, PermissionRequiredMixin, BaseDirView):
    permission_required = 'task.view_docs'

    def __init__(self, *args, **kwargs):
        self.template_name = 'docs/folder.html'
        super().__init__(app, *args, **kwargs)
        self.storage_path = settings.DJANGO_STORAGE_PATH

    def get(self, request, *args, **kwargs):
        query = None
        folder = ''
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
            folder = self.request.GET.get('folder')
        if query:
            if folder:
                folder = '&folder=' + folder
            else:
                folder = ''
            return HttpResponseRedirect(reverse('index') + '?app=docs' + folder + '&q=' + query)
        ret = super().get(request, *args, **kwargs)
        return ret

    def get_context_data(self, **kwargs):
        self.store_dir = self.storage_path.format(self.request.user.username) + 'docs/'
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/docs'
        context['add_item_template'] = 'core/add_item_upload.html'
        context['add_item_placeholder'] = '{}'.format(_('Upload document'))
        return context

    def get_success_url(self, **kwargs):
        folder = ''
        if ('folder' in self.request.GET):
            folder = self.request.GET['folder']
        return reverse('docs:list') + '?folder=' + folder

def get_name_from_request(request, param='file'):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get(param)
    if not query:
        return ''
    return urllib.parse.unquote_plus(query)

@login_required(login_url='account:login')
@permission_required('task.view_docs')
def get_file(request):
    try:
        storage_path = settings.DJANGO_STORAGE_PATH
        store_dir = storage_path.format(request.user.username) + 'docs/'
        folder = get_name_from_request(request, 'folder')
        file = get_name_from_request(request, 'file')
        filepath = store_dir + folder + '/' + file
        fsock = open(filepath, 'rb')
        response = FileResponse(fsock)
        return response
    except IOError:
        return HttpResponseNotFound()
