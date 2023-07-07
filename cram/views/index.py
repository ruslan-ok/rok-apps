from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cram.context import CramContext
from cram.config import app_config
from task.const import APP_CRAM, ROLE_CRAM
from task.models import Group
from cram.models import Phrase

app = APP_CRAM
role = ROLE_CRAM

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, CramContext):
    #template_name = "cram/index.html"
    permission_required = 'cram.view_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CRAM)

    def get_template_names(self):
        if 'group' in self.request.GET:
            return ['cram/phrase_list.html']
        return ['cram/index.html']

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        # if not request.user.is_authenticated:
        #     return ret
        # active_group = self.get_active_group(self.config.cur_view_group)
        # if ('group' not in request.GET) and self.config.cur_view_group:
        #     self.
        #     if not Group.objects.filter(user=request.user.id, app=self.config.cur_view_group.app, determinator=self.config.cur_view_group.determinator).exists():
        #         return ret
        #     nav_item = Group.objects.filter(user=request.user.id, app=app, role=ROLE_CRAM)[0]
        #     if nav_item:
        #         return HttpResponseRedirect(request.path + '?group=' + str(nav_item.id))
        return ret

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('Cram')
        context['add_item_template'] = 'cram/add_item_input.html'
        # group = self.get_cur_group()
        # phrase = None
        # if group and Phrase.objects.filter(user=self.request.user.id, grp=group).exists():
        #     phrase = Phrase.objects.filter(user=self.request.user.id, grp=group).order_by('sort')[0]
        # context['group'] = group
        # context['phrase'] = phrase
        return context

