import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cram.context import CramContext
from cram.config import app_config
from task.const import APP_CRAM, ROLE_CRAM
from cram.models import CramGroup, Lang, Phrase, LangPhrase

app = APP_CRAM
role = ROLE_CRAM

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, CramContext):
    permission_required = 'cram.view_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CRAM)

    def get_template_names(self):
        if 'group' in self.request.GET:
            return ['cram/phrase_list.html']
        return ['cram/index.html']

    def get_queryset(self):
        if 'group' in self.request.GET:
            grp_id = int(self.request.GET.get('group', '0'))
            if CramGroup.objects.filter(user=self.request.user.id, id=grp_id).exists():
                grp = CramGroup.objects.filter(user=self.request.user.id, id=grp_id).get()
                return Phrase.objects.filter(user=self.request.user.id, grp=grp.id).order_by('sort')
        return []

    def post(self, request, *args, **kwargs):
        grp = None
        text = ''
        p_phrase = ''
        if 'group' in self.request.GET:
            grp_id = int(self.request.GET.get('group', '0'))
            if CramGroup.objects.filter(user=self.request.user.id, id=grp_id).exists():
                grp = CramGroup.objects.filter(user=self.request.user.id, id=grp_id).get()
        if 'add_item_name' in self.request.POST:
            text = self.request.POST.get('add_item_name', '')
        if grp and text:
            sort = 1
            if Phrase.objects.filter(user=request.user.id, grp=grp).exists():
                sort = Phrase.objects.filter(user=request.user.id, grp=grp).order_by('-sort')[0].sort + 1
            phrase = Phrase.objects.create(user=self.request.user, grp=grp, sort=sort)
            lang = Lang.objects.filter(user=self.request.user, code='ru').get()
            LangPhrase.objects.create(phrase=phrase, lang=lang, text=text)
            p_phrase = f'&phrase={phrase.id}'
        return HttpResponseRedirect(reverse('cram:list') + f'?group={grp_id}{p_phrase}')

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('Cram')
        context['add_item_template'] = 'cram/add_item_input.html'
        objects = []
        sel_phrase = None
        phrase_id = 0
        if 'phrase' in self.request.GET:
            phrase_id = int(self.request.GET.get('phrase', '0'))
        for phrase in self.get_queryset():
            p = {
                'id': phrase.id,
                'active': (phrase.id == phrase_id),
                'name': phrase.name(),
                'data': [],
            }
            for lang_code in ('ru', 'en', 'pl'):
                text = ''
                lang_phrase_id = 0
                if Lang.objects.filter(user=self.request.user.id, code=lang_code).exists():
                    lang = Lang.objects.filter(user=self.request.user.id, code=lang_code).get()
                    if LangPhrase.objects.filter(phrase=phrase.id, lang=lang.id).exists():
                        lp = LangPhrase.objects.filter(phrase=phrase.id, lang=lang.id).get()
                        lang_phrase_id = lp.id
                        if lp.text:
                            text = lp.text
                l = {
                    'id': lang_phrase_id,
                    'lang': lang_code,
                    'text': text,
                }
                p['data'].append(l)
            if (phrase.id == phrase_id):
                sel_phrase = p
            objects.append(p)
        if not sel_phrase and len(objects):
            sel_phrase = objects[0]
        context['object_list'] = objects
        context['sel_phrase'] = sel_phrase
        context['django_host_api'] = os.environ.get('DJANGO_HOST_API', 'http://localhost:8000')
        return context

