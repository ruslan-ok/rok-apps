import urllib, os
from PIL import Image
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, FileResponse
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from rusel.base.context import Context
from family.models import (FamTree, FamTreeUser, FamRecord, IndividualRecord, MultimediaRecord, RepositoryRecord, 
    NoteStructure, SourceRecord, SubmitterRecord, Params, IndiInfo)
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
                case 'individual': return IndiInfo.objects.filter(tree_id=tree_id)
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

class GenealogyDetailsView(UpdateView, GenealogyContext, LoginRequiredMixin):

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

