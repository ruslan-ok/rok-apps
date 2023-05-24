from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rusel.base.views import Context
from cram.config import app_config
from cram.models import Phrase
from cram.forms import CreateForm, EditForm
from task.const import ROLE_CRAM, ROLE_APP
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from cram.get_info import get_info

role = ROLE_CRAM
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Phrase
    form_class = CreateForm
    permission_required = 'cram.view_phrase'

    def __init__(self):
        super().__init__(app_config, role)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return []
        data = Phrase.objects.filter(user=self.request.user.id)
        return data

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Phrase
    form_class = EditForm
    permission_required = 'cram.change_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response



# class PhraseView(Context):
#     def __init__(self, request):
#         super().__init__()
#         self.object = None
#         self.request = request
#         self.set_config(app_config, 'overview')
#         self.config.set_view(request)

#     def get_dataset(self, group, query=None, nav_item=None):
#         return Phrase.objects.filter(user=self.request.user.id)

# def phrases(request):
#     view = PhraseView(request)
#     context = view.get_app_context(request.user.id)
#     return render(request, 'cram/phrases.html', context=context)

# def phrase(request, pk):
#     return render(request, 'cram/phrase.html', context={})

class GroupView(LoginRequiredMixin, BaseGroupView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def training(request):
    return render(request, 'cram/training.html', context={})


