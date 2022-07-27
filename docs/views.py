import urllib.parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from task.const import APP_DOCS, ROLE_DOC, ROLE_APP
from rusel.base.dir_views import BaseDirView
from rusel.files import storage_path
from docs.config import app_config

role = ROLE_DOC
app = ROLE_APP[role]

class FolderView(LoginRequiredMixin, BaseDirView):
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        self.template_name = 'docs/folder.html'
        super().__init__(app_config, role, *args, **kwargs)

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
            return HttpResponseRedirect(reverse('index') + '?app=' + APP_DOCS + folder + '&q=' + query)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.store_dir = storage_path.format(self.request.user.username) + 'docs/'
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/docs/'
        context['add_item_template'] = 'base/add_item_upload.html'
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

def get_file(request):
    try:
        store_dir = storage_path.format(request.user.username) + 'docs/'
        folder = get_name_from_request(request, 'folder')
        file = get_name_from_request(request, 'file')
        filepath = store_dir + folder + '/' + file
        fsock = open(filepath, 'rb')
        response = FileResponse(fsock)
        return response
    except IOError:
        return HttpResponseNotFound()
