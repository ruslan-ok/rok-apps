import random
from datetime import datetime
from difflib import HtmlDiff, SequenceMatcher
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.context import AppContext
from cram.models import CramGroup, Lang, Phrase, LangPhrase, Training, TrainingPhrase
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
        context['hide_add_item_input'] = True
        group_id = int(self.kwargs.get('group', '0'))
        phrase_id = int(self.kwargs.get('phrase', '0'))
        group = CramGroup.objects.filter(user=self.request.user.id, id=group_id).get()
        context['config'] = {'app_title': _('Cram training')}
        context['title'] = group.name
        session = self.check_session(self.request.user, group_id)

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
        context['statist'] = get_statist(session, phrase_id)
        context['session'] = session
        return context
    
    def check_session(self, user, group_id):
        sessions = Training.objects.filter(user=user.id, group=group_id, stop=None)
        if sessions.count():
            session = sessions[0]
        else:
            group = CramGroup.objects.filter(user=user.id, id=group_id).get()
            phrases = Phrase.objects.filter(user=user.id, group=group_id)
            session = Training.objects.create(user=user, group=group, start=datetime.now(), stop=None, total=phrases.count(), ratio=0.0, passed=0)
        return session

    
    def post(self, request, *args, **kwargs):
        group_id = int(self.kwargs.get('group', '0'))
        phrase_id = int(self.kwargs.get('phrase', '0'))
        phrase = Phrase.objects.filter(user=request.user.id, group=group_id, id=phrase_id).get()
        session = self.check_session(self.request.user, group_id)
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
            if not TrainingPhrase.objects.filter(training=session.id, phrase=phrase.id, lang=lang.id).exists():
                TrainingPhrase.objects.create(training=session, phrase=phrase, lang=lang, ratio=value['ratio'])
        kwargs['values'] = values
        return self.get(request, *args, **kwargs)
    
def training_start(request, group):
    phrases = Phrase.objects.filter(user=request.user.id, group=group)
    if not phrases.count():
        return HttpResponseRedirect(reverse('cram:phrases', args=(group,)))
    for session in Training.objects.filter(user=request.user.id, group=group, stop=None):
        session.stop = datetime.now()
        session.save()
    phrases = list(phrases)
    random.shuffle(phrases)
    for idx, p in enumerate(phrases):
        p.sort = idx
        p.save()
    first_phrase = phrases[0]
    return HttpResponseRedirect(reverse('cram:training', args=(group, first_phrase.id)))

def training_stop(request, group):
    for session in Training.objects.filter(user=request.user.id, group=group, stop=None):
        session.stop = datetime.now()
        session.save()
    phrases = Phrase.objects.filter(user=request.user.id, group=group)
    for p in phrases:
        p.sort = p.id
        p.save()
    return HttpResponseRedirect(reverse('cram:phrases', args=(group,)))

def get_statist(session, active_phrase_id=0):
    statist = []
    all_total = all_correct = 0
    for lang in session.group.get_languages():
        if lang.code == 'ru':
            continue
        total = correct = 0
        ls = {
            'code': lang.code,
            'steps': [],
            'ratio': None,
        }
        for phrase in Phrase.objects.filter(user=session.user.id, group=session.group.id).order_by('sort'):
            color = 'white'
            icon = 'stop'
            if TrainingPhrase.objects.filter(training=session.id, phrase=phrase.id, lang=lang.id).exists():
                icon = 'stop-fill'
                phrase_ratio = TrainingPhrase.objects.filter(training=session.id, phrase=phrase.id, lang=lang.id).get()
                total += 1
                all_total += 1
                if phrase_ratio.ratio == 1:
                    color = 'green'
                    correct += 1
                    all_correct += 1
                else:
                    color = 'red'
            elif phrase.id == active_phrase_id:
                    icon = 'stop-fill'
                    color = 'black'
            ls['steps'].append({
                'id': phrase.id,
                'icon': icon,
                'color': color
            })
        if total:
            ls['ratio'] = correct / total
        statist.append(ls)
    if all_total:
        session.ratio = all_correct / all_total
        session.save()
    return statist

