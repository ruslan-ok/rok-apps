import urllib, os, glob, re
from PIL import Image
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, FileResponse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView, FormMixin
from django.shortcuts import get_object_or_404
from rusel.base.context import Context
from rusel.base.dir_forms import UploadForm
from rusel.utils import extract_get_params
from family.models import FamTree, FamTreeUser, FamRecord, IndividualRecord, MultimediaRecord, RepositoryRecord, NoteStructure, SourceRecord, SubmitterRecord, Params
from family.config import app_config


class GenealogyContext(Context):
    def get_dataset(self, group, query=None, nav_item=None):
        if group:
            if group.view_id == 'pedigree':
                return FamTreeUser.objects.filter(user_id=self.request.user.id)
            tree = Params.get_cur_tree(self.request.user)
            if not tree:
                return []
            tree_id = int(tree.id)
            match group.view_id:
                case 'family': return FamRecord.objects.filter(tree=tree_id)
                case 'media': return MultimediaRecord.objects.filter(tree=tree_id)
                case 'repo': return RepositoryRecord.objects.filter(tree=tree_id)
                case 'note': return NoteStructure.objects.filter(tree=tree_id)
                case 'source': return SourceRecord.objects.filter(tree=tree_id)
                case 'submitter': return SubmitterRecord.objects.filter(tree=tree_id)

        return []

    def get_app_context(self, user_id, search_qty=None, icon=None, nav_items=None, role=None):
        self.config.set_view(self.request)
        context = super().get_app_context(user_id, search_qty, icon, nav_items)
        cur_tree = Params.get_cur_tree(self.request.user)
        if cur_tree:
            context['current_group'] = str(cur_tree.id)
        context['api_role'] = 'famtree'
        return context

class GenealogyListView(ListView, GenealogyContext, LoginRequiredMixin):

    def __init__(self):
        super().__init__()
        self.set_config(app_config, 'tree')

    def get_context_data(self):
        context = super().get_context_data()
        self.config.set_view(self.request)
        upd_context = self.get_app_context(self.request.user.id, icon=self.config.view_icon)
        context.update(upd_context)
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            context['tree_id'] = tree_id
        return context

class GenealogyDetailsView(UpdateView, GenealogyContext, LoginRequiredMixin, FormMixin):

    def __init__(self):
        super().__init__()
        self.set_config(app_config, 'tree')

    def get_success_url(self):
        if ('form_close' in self.request.POST):
            return reverse('family:pedigree-list') + extract_get_params(self.request, None)
        return reverse('family:pedigree-detail', args=(self.object.id,)) + extract_get_params(self.request, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.config.set_view(self.request)
        upd_context = self.get_app_context(self.request.user.id, icon=self.config.view_icon)
        context.update(upd_context)
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            context['tree_id'] = tree_id
        return context

    def tune_dataset(self, data, group):
        return data

           
def photo(request, ft):
    file = get_name_from_request(request, 'file')
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=ft))
    tree = get_object_or_404(FamTree.objects.filter(id=ft))
    storage_path = os.environ.get('DJANGO_STORAGE_PATH', '')
    media_path = storage_path.format('family_tree') + tree.store_name()
    fsock = open(media_path + '/' + file, 'rb')
    return FileResponse(fsock)

def scaled_image(mmr: MultimediaRecord, size: int) -> HttpResponse:
    file = mmr.get_file()
    storage_path = os.environ.get('DJANGO_STORAGE_PATH', '')
    media_path = storage_path.format('family_tree') + mmr.tree.store_name()
    img = Image.open(media_path + '/' + file)
    if mmr._posi:
        box = tuple([int(x) for x in mmr._posi.split(' ')])
        img = img.crop(box)
    thumb_size = (size, size, )
    img.thumbnail(thumb_size)
    format = mmr.get_format()
    response = HttpResponse(content_type='image/' + format)
    img.save(response, format)
    return response

def thumbnail(request, ft, size=44):
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=ft))
    tree = get_object_or_404(FamTree.objects.filter(id=ft))
    mmr_id = get_name_from_request(request, 'mmr')
    mmr = get_object_or_404(MultimediaRecord.objects.filter(id=mmr_id, tree=tree.id))
    if mmr:
        return scaled_image(mmr, size)
    return default_avatar(size)

def thumbnail_100(request, ft):
    return thumbnail(request, ft, 100)

def get_name_from_request(request, param='file'):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get(param)
    if not query:
        return ''
    return urllib.parse.unquote_plus(query)

@login_required(login_url='account:login')
def avatar(request, ft, pk):
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=ft))
    get_object_or_404(FamTree.objects.filter(id=ft))
    indi = get_object_or_404(IndividualRecord.objects.filter(id=pk))
    mmr = indi.get_avatar_mmr()
    if mmr:
        return scaled_image(mmr, 150)
    return default_avatar(150)

def default_avatar(size: int) -> HttpResponse:
    static_path = os.environ.get('DJANGO_STATIC_ROOT', '')
    img = Image.open(static_path + '/Default-avatar.jpg')
    thumb_size = (size, size, )
    img.thumbnail(thumb_size)
    response = HttpResponse(content_type='image/jpeg')
    img.save(response, 'jpeg')
    return response

class UploadGedcomView(FormView, GenealogyContext, LoginRequiredMixin):
    form_class = UploadForm
    file: str

    def __init__(self):
        super().__init__()
        self.file = ''

    def get_success_url(self):
        return reverse_lazy('family:pedigree-import') + '?file=' + self.file

    def post(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('upload')
        if form.is_valid():
            for f in files:
                self.handle_uploaded_file(request.user, f)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def avoid_duplication(self, f):
        file_parts = os.path.splitext(f)
        file_path = '\\'.join(file_parts[0].split('\\')[:-1])
        file_name = file_parts[0].split('\\')[-1]
        file_name_base = file_name
        file_ext = file_parts[1][1:]
        num = 0
        x = re.fullmatch(r'(.*) \((\d+)\)', file_name)
        if x:
            file_name = x[1]
            num = int(x[2])
        files = glob.glob(file_path + '\\' + file_name + '*.' + file_ext)
        for file in files:
            file_parts = os.path.splitext(file)
            file_name_cmp = file_parts[0].split('\\')[-1]
            if file_name_cmp == file_name_base and num == 0:
                num = 1
            else:
                x = re.fullmatch(r'(.*) \((\d+)\)', file_name_cmp)
                if x:
                    file_name = x[1]
                    if num <= int(x[2]):
                        num = int(x[2]) + 1
        if num == 0:
            return f'{file_path}\\{file_name}.{file_ext}'
        return f'{file_path}\\{file_name} ({num}).{file_ext}'

    def handle_uploaded_file(self, user, f):
        path = FamTree.get_import_path()
        filepath = self.avoid_duplication(path + f.name)
        with open(filepath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        self.file = filepath.split('\\')[-1]
