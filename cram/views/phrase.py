from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from task.const import APP_CRAM, ROLE_LANG, ROLE_CRAM
from cram.models import *
from cram.forms.language import CreateForm, EditForm
from cram.config import app_config
from cram.context import CramContext

app = APP_CRAM
role = ROLE_LANG

class PhraseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView, CramContext):
    model = Phrase
    form_class = CreateForm
    permission_required = 'cram.view_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, role)

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return ret
        if ('group' not in request.GET):
            if not Group.objects.filter(user=request.user.id, app=app, role=ROLE_CRAM).exists():
                return ret
            nav_item = Group.objects.filter(user=request.user.id, app=app, role=ROLE_CRAM)[0]
            if nav_item:
                return HttpResponseRedirect(request.path + '?group=' + str(nav_item.id))
        return ret

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('List of phrases')
        context['languages'] = Lang.objects.all()
        return context

class PhraseDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, CramContext):
    model = LangPhrase
    form_class = EditForm
    permission_required = 'cram.change_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, role)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.role_info()
        return response





# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _
# from rusel.base.views import Context
# from cram.config import app_config
# from cram.models import Phrase
# from cram.forms import CreateForm, EditForm
# from task.const import ROLE_CRAM, ROLE_APP
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
# from cram.get_info import get_info

# role = ROLE_CRAM
# app = ROLE_APP[role]

# class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
#     model = Phrase
#     form_class = CreateForm
#     permission_required = 'cram.view_phrase'

#     def __init__(self):
#         super().__init__(app_config, role)

#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return []
#         data = Phrase.objects.filter(user=self.request.user.id)
#         return data

# class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
#     model = Phrase
#     form_class = EditForm
#     permission_required = 'cram.change_phrase'

#     def __init__(self, *args, **kwargs):
#         super().__init__(app_config, role, *args, **kwargs)

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         get_info(form.instance)
#         return response



# # class PhraseView(Context):
# #     def __init__(self, request):
# #         super().__init__()
# #         self.object = None
# #         self.request = request
# #         self.set_config(app_config, 'overview')
# #         self.config.set_view(request)

# #     def get_dataset(self, group, query=None, nav_item=None):
# #         return Phrase.objects.filter(user=self.request.user.id)

# # def phrases(request):
# #     view = PhraseView(request)
# #     context = view.get_app_context(request.user.id)
# #     return render(request, 'cram/phrases.html', context=context)

# # def phrase(request, pk):
# #     return render(request, 'cram/phrase.html', context={})

# class GroupView(LoginRequiredMixin, BaseGroupView):

#     def __init__(self, *args, **kwargs):
#         super().__init__(app_config, role, *args, **kwargs)

# def training(request):
#     return render(request, 'cram/training.html', context={})


