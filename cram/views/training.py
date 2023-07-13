from difflib import HtmlDiff, SequenceMatcher
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.context import AppContext
from cram.models import CramGroup, Lang, Phrase, LangPhrase
from task.const import APP_CRAM, ROLE_CRAM

class TrainingView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "cram/training.html"
    permission_required = 'cram.view_phrase'

    def get_queryset(self):
        group_id = int(self.kwargs.get('group', '0'))
        return Phrase.objects.filter(user=self.request.user.id, group=group_id).order_by('sort')
    
    def get_context_data(self, **kwargs):
        app_context = AppContext(self.request.user, APP_CRAM, ROLE_CRAM)
        context = app_context.get_context()
        context['title'] = _('Cram training')
        context['hide_add_item_input'] = True
        group_id = int(self.kwargs.get('group', '0'))
        phrase_id = int(self.kwargs.get('phrase', '0'))
        group = CramGroup.objects.filter(user=self.request.user.id, id=group_id).get()
        test_phrase = []
        for lang in group.get_languages():
            lp = None
            check_text = text_diff = check_diff = status = ''
            if 'values' in kwargs and lang.code in kwargs['values']:
                status = kwargs['values'][lang.code].get('status', '')
                check_text = kwargs['values'][lang.code].get('check', '')
                text_diff = kwargs['values'][lang.code].get('text_diff', '')
                check_diff = kwargs['values'][lang.code].get('check_diff', '')
            if LangPhrase.objects.filter(phrase=phrase_id, lang=lang.id).exists():
                lp = LangPhrase.objects.filter(phrase=phrase_id, lang=lang.id).get()
            if lp:
                x = {
                    'lang': lang.code,
                    'id': lp.id,
                    'text': lp.text,
                    'check_text': check_text,
                    'status': status,
                    'text_diff': text_diff,
                    'check_diff': check_diff,
                }
            else:
                x = {
                    'lang': lang.code,
                    'id': None,
                    'text': '',
                }
            test_phrase.append(x)
        context['test_phrase'] = test_phrase
        object_list = self.get_queryset()
        context['group_id'] = group_id
        context['object_list'] = object_list
        prev_phrase_id = next_phrase_id = 0
        found = False
        npp = 0
        for x in object_list:
            npp += 1
            if found and not next_phrase_id:
                next_phrase_id = x.id
                break
            if not found and x.id == phrase_id:
                found = True
                context['curr_pos'] = npp
            else:
                prev_phrase_id = x.id
        context['active_id'] = phrase_id
        context['prev_phrase_id'] = prev_phrase_id
        context['next_phrase_id'] = next_phrase_id
        context['token'] = self.get_token(self.request)
        return context
    
    def get_token(self, request):
        value = request.COOKIES.get('training_token')
        if value is None:
            value = '???'
        return value

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        value = self.get_token(request)
        response.set_cookie('training_token', value)
        return response

    def post(self, request, *args, **kwargs):
        values = {}
        d = HtmlDiff()
        for lang in Lang.objects.filter(user=request.user.id):
            if lang.code == 'ru' or not request.POST.get(lang.code + '_check_text', ''):
                continue
            value = {
                'text': request.POST.get(lang.code + '_text', ''),
                'check': request.POST.get(lang.code + '_check_text', ''),
            }
            s = SequenceMatcher(None, value['text'], value['check'])
            value['ratio'] = s.ratio()
            if value['ratio'] == 1.0:
                value['status'] = 'correct'
            else:
                value['status'] = 'incorrect'
                cmp = d.make_table([value['text']], [value['check']])
                tds = cmp.split('</td>')
                value['text_diff'] = tds[2].replace('<td nowrap="nowrap">', '')
                value['check_diff'] = tds[5].replace('<td nowrap="nowrap">', '')
            values[lang.code] = value
        kwargs['values'] = values
        return self.get(request, *args, **kwargs)
