import os
import pandas as pd
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from task.const import APP_CRAM, ROLE_CRAM
from core.context import AppContext
from cram.models import *
from rusel.context import get_group_path

class PhrasesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Phrase
    permission_required = 'cram.view_phrase'
    template_name = 'cram/phrases.html'

    def get_queryset(self):
        group_id = int(self.kwargs.get('group', '0'))
        return Phrase.objects.filter(user=self.request.user.id, group=group_id).order_by('sort')

    def post(self, request, *args, **kwargs):
        group = None
        text = ''
        group_id = int(self.kwargs.get('group', '0'))
        if group_id:
            if CramGroup.objects.filter(user=self.request.user.id, id=group_id).exists():
                group = CramGroup.objects.filter(user=self.request.user.id, id=group_id).get()
        if 'add_item_name' in self.request.POST:
            text = self.request.POST.get('add_item_name', '')
        if group and text:
            sort = 1
            if Phrase.objects.filter(user=request.user.id, group=group_id).exists():
                sort = Phrase.objects.filter(user=request.user.id, group=group_id).order_by('-sort')[0].sort + 1
            phrase = Phrase.objects.create(user=self.request.user, group=group, sort=sort)
            phrase.correct_groups_qty(GroupQuantityCorrectMode.ADD_PHRASE, group_id)
            lang = Lang.objects.filter(user=self.request.user, code='ru').get()
            LangPhrase.objects.create(phrase=phrase, lang=lang, text=text)
        return HttpResponseRedirect(reverse('cram:phrases', args=(group_id, phrase.id)))

    def get_context_data(self, **kwargs):
        app_context = AppContext(self.request.user, APP_CRAM, ROLE_CRAM)
        context = app_context.get_context()
        group_id = int(self.kwargs.get('group', '0'))
        phrase_id = int(self.kwargs.get('phrase', '0'))
        context['group_id'] = group_id
        context['phrase_id'] = phrase_id
        group = CramGroup.objects.filter(user=self.request.user.id, id=group_id).get()
        context['title'] = f'Список фраз "{group.name}"'
        context['group_path'] = get_group_path(group.id)
        context['add_item_template'] = 'cram/add_item_input.html'
        objects = []
        sel_phrase = None
        for phrase in self.get_queryset():
            p = {
                'id': phrase.id,
                'active': (phrase.id == phrase_id),
                'name': phrase.name(),
                'data': [],
            }
            for lang in group.get_languages():
                text = ''
                lang_phrase_id = 0
                if LangPhrase.objects.filter(phrase=phrase.id, lang=lang.id).exists():
                    lp = LangPhrase.objects.filter(phrase=phrase.id, lang=lang.id).get()
                    lang_phrase_id = lp.id
                    if lp.text:
                        text = lp.text
                l = {
                    'id': lang_phrase_id,
                    'lang': lang.code,
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

data_file = 'C:\\Web\\lang\\data.csv'

def import_phrases(request, group):
    df = pd.read_csv(data_file)
    ru_lang = Lang.objects.filter(user=request.user.id, code='ru').get()
    pl_lang = Lang.objects.filter(user=request.user.id, code='pl').get()
    for group_id in df[df['group'] != df['group'].isnull()]['group'].dropna().unique():
        if int(group_id) != group or not CramGroup.objects.filter(id=int(group_id)).exists():
            continue
        group_obj = CramGroup.objects.filter(id=int(group_id)).get()
        sort = 1
        if Phrase.objects.filter(user=request.user).exists():
            sort = Phrase.objects.filter(user=request.user).order_by('-sort')[0].sort + 1
        for index, row in df[df['group'] == group_id].dropna().iterrows():
            phrase = Phrase.objects.create(user=request.user, group=group_obj, sort=sort)
            phrase.correct_groups_qty(GroupQuantityCorrectMode.ADD_PHRASE, group_obj.id)
            sort += 1
            LangPhrase.objects.create(phrase=phrase, lang=ru_lang, text=row['ru_text'])
            LangPhrase.objects.create(phrase=phrase, lang=pl_lang, text=row['pl_text'])
    return HttpResponseRedirect(reverse('cram:phrases', args=(group,)))