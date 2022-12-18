from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import (CreateIndiForm, EditIndiEssentials, )
from family.models import (FamTreeUser, IndiInfo, IndiFamilies, IndiSpouses, )

EXTRA_FIXES = [
    ('essentials', _('essentials')),
    ('family', _('family')),
    ('biography', _('biography')),
    ('contacts', _('contact info')),
    ('work', _('work')),
    ('education', _('education')),
    ('favorites', _('favorites')),
    ('pers_info', _('personal info')),
    ('citation', _('source citation')),
    ('facts', _('all facts')),
]

class IndiListView(GenealogyListView):
    model = IndiInfo
    form_class = CreateIndiForm
    template_name = 'family/individual/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return IndiInfo.objects.filter(tree_id=tree_id)
        return []

class IndiDetailsView(GenealogyDetailsView):
    model = IndiInfo
    form_class = EditIndiEssentials
    template_name = 'family/individual/essentials.html'

    def get(self, request, ft, pk, view=None):
        if not request.user.is_authenticated:
            raise Http404
        cur_view = view
        extra_fixes_keys = [x[0] for x in EXTRA_FIXES]
        if (cur_view not in extra_fixes_keys):
            return HttpResponseRedirect(reverse('family:individual-view', args=(ft, pk, 'essentials', )))
        self.template_name = f'family/individual/{cur_view}.html'
        ret = super().get(request)
        return ret

    def get_context_data(self):
        context = super().get_context_data()
        context['extra_fix_list'] = self.get_extra_fixes()
        context['indi_id'] = self.get_object().id
        cur_view = self.request.GET.get('view')
        match cur_view:
            case 'essentials': pass
            case 'family':
                context['family'] = IndiFamilies.objects.filter(chil_id=self.get_object().id)
                context['spouses'] = self.get_spouses()
            case 'biography': pass
            case 'contacts': pass
            case 'work': pass
            case 'education': pass
            case 'favorites': pass
            case 'pers_info': pass
            case 'citation': pass
            case 'facts': pass
        return context

    def get_spouses(self):
        spouses = IndiSpouses.objects.filter(indi_id=self.get_object().id)
        ret = []
        spouse_id = None
        sp = {}
        for spouse in spouses:
            if spouse.spou_id != spouse_id:
                if spouse_id:
                    ret.append(sp)
                spouse_id = spouse.spou_id
                sp = {
                    'id': spouse.spou_id,
                    'givn': spouse.givn,
                    'surn': spouse.surn,
                    'role': '???',
                    'relation': '???',
                    'spou_thumbnail': spouse.spou_thumbnail(),
                    'events': [],
                }
            ev = {
                'date_label': _('date'),
                'date': spouse.date,
                'place_label': _('place'),
                'place': spouse.plac,
                'witnesses_label': _('witnesses'),
                'witnesses': 'spouse.witnesses',
            }
            sp['events'].append(ev)
        if spouse_id:
            ret.append(sp)
        return ret

    def get_extra_fixes(self):
        fixes = []
        for fix in EXTRA_FIXES:
            fixes.append({
                'determinator': 'view',
                'id': fix[0],
                'url': reverse('family:individual-view', args=(int(self.kwargs.get('ft')), self.get_object().id, fix[0],)),
                'title': _(fix[1]).capitalize(),
                'active': (self.kwargs.get('view') == fix[0]),
            })
        return fixes
