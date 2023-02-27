import json
from datetime import datetime
from typing import List
from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import date_format
from family.ged4py.date import DateValue
from family.views.base import GenealogyDetailsView
from family.forms import EditIndividualForm
from family.models import IndividualRecord, IndividualEventStructure
from family.descriptions.individual import DescriptorIndi
from family.descriptions.event import DescriptorEvent

@dataclass
class IndiRole:
    role: str
    indi: IndividualRecord

@dataclass
class IndiEvent:
    indi: IndiRole
    event: IndividualEventStructure

    def get_str_date(self):
        if self.event.deta:
            ev_date = DateValue.parse(self.event.deta.date)
            if ev_date:
                return ev_date.get_str_date()
        return ''

    def get_type_name(self):
        match self.indi.role, self.indi.indi.get_sex(), self.event.tag:
            case 'indi', _, 'BIRT': ret = _('Birth')
            case 'indi', _, 'DEAT': ret = _('Death')
            case 'father', _, 'DEAT': ret = _('Death of father')
            case 'mother', _, 'DEAT': ret = _('Death of mother')
            case 'spouse', 'F', 'DEAT': ret = _('Death of wife')
            case 'spouse', 'M', 'DEAT': ret = _('Death of husband')
            case 'child', 'F', 'BIRT': ret = _('Birth of daughter')
            case 'child', 'M', 'BIRT': ret = _('Birth of son')
            case 'child', 'F', 'DEAT': ret = _('Death of daughter')
            case 'child', 'M', 'DEAT': ret = _('Death of son')
            case _: ret = f'? {self.indi.role} {self.indi.indi.get_sex()} {self.event.tag}'
        return ret
    
    def get_info(self, birth_str_date, indi, person):
        raw_date = self.get_str_date()
        full = day_month = year = ''
        try:
            dt = datetime.strptime(raw_date, '%Y-%m-%d')
            full = date_format(dt, format='DATE_FORMAT', use_l10n=True)
            day_month = dt.strftime('%d %b')
            year = dt.strftime('%Y')
        except:
            try:
                year = int(raw_date)
                full = str(year)
            except:
                pass
        when = ''
        if day_month:
            when = pgettext_lazy('event date', 'on %(date)s') % {'date': full}
        elif year:
            when = pgettext_lazy('event date', 'in %(date)s') % {'date': str(year)}
        date = {
            'full': full,
            'when': when,
            'sort': raw_date,
            'day_month': day_month,
            'year': year,
        }
        match self.event.tag:
            case 'DEAT': extra = '1'
            case 'BURI': extra = '2'
            case _: extra = '0'
        event_place = ''
        event_map = None
        if self.event.deta and self.event.deta.plac:
            event_place = self.event.deta.plac.name
            if self.event.deta.plac.map_lati and self.event.deta.plac.map_long:
                event_map = (self.event.deta.plac.map_lati, self.event.deta.plac.map_long)
        descr = DescriptorEvent(self.indi.indi, self.indi.role, self.event)
        return {
            'id': self.indi.indi.get_id(),
            'role': self.indi.role,
            'tag': self.event.tag,
            'date': date,
            'age': self.indi.indi.get_age(raw_date, birth_str_date),
            'sort': raw_date + '-ex-' + extra,
            'type_name': self.get_type_name(),
            'bg_white': False,
            'descr': descr.get_descr(date, indi),
            'person': person,
            'place': event_place,
            'map': event_map,
        }

class IndividualDetailsView(GenealogyDetailsView, LoginRequiredMixin, PermissionRequiredMixin):
    model = IndividualRecord
    form_class = EditIndividualForm
    template_name = 'family/individual/life.html'
    permission_required = 'family.change_pedigree'

    def get_template_names(self) -> List[str]:
        ret = super().get_template_names()
        view = self.kwargs.get('view', '')
        if view:
            ret = [f'family/individual/{view}.html']
        return ret
    
    def get_life_info(self, indi: IndividualRecord):
        indi_list = []
        indi_list.append(IndiRole('indi', indi))
        father, mother = indi.get_parents()
        if father:
            indi_list.append(IndiRole('father', father))
        if mother:
            indi_list.append(IndiRole('mother', mother))
        for spouse in indi.get_spouses():
            indi_list.append(IndiRole('spouse', spouse))
        for child in indi.get_children():
            indi_list.append(IndiRole('child', child))
        events = []
        birth = death = None
        birth_str_date = ''
        for x in indi_list:
            for event in x.indi.get_events():
                ev = IndiEvent(x, event)
                if x.role == 'spouse' and event.tag == 'BIRT':
                    continue
                if ev.get_str_date():
                    events.append(ev.get_info(birth_str_date, indi, x.indi))
                    match x.role, event.tag:
                        case 'indi', 'BIRT': 
                                birth = ev
                                birth_str_date = ev.get_str_date()
                        case 'indi', 'DEAT': death = ev
        events = [x for x in sorted(events, key=lambda x: x['sort']) if (x['tag'] != 'BURI') and (not birth or x['date']['sort'] >= birth.get_str_date()) and (not death or x['date']['sort'] <= death.get_str_date())]
        points = []
        for event in events:
            if event['map']:
                name = str(event['type_name'])
                if event['person']:
                    name += ' ' + event['person'].get_name('given')
                points.append({
                    'id': event['id'],
                    'name': name,
                    'date': event['date']['when'],
                    'place': event['place'],
                    'lat': event['map'][0], 
                    'lon': event['map'][1], 
                })
        total_num = len(events)
        ret = []
        for num, ev in enumerate(events):
            ev['bg_white'] = (num == 0)
            ev['is_last'] = (num == (total_num-1))
            ret.append(ev)
        father, mother = indi.get_parents()
        descr = DescriptorIndi(indi)
        biography = descr.get_biography()
        ret = {
            'biography': biography,
            'family_title': '???',
            'indi_family': {
                'indi_id': indi.get_id(),
                'indi_sex': indi.get_sex(),
                'indi_full_name': indi.get_name(),
                'map_title': '???',
                'fig_caption': '???',
            },
            'children': indi.get_children(),
            'spouses': indi.get_spouses(),
            'events': events,
            'map_points': json.dumps(points),
        }
        if father:
            ret['indi_family']['father_id'] = father.get_id()
            ret['indi_family']['father_sex'] = father.get_sex()
            ret['indi_family']['father_full_name'] = father.get_name()
        else:
            ret['indi_family']['father_id'] = 0
            ret['indi_family']['father_sex'] = 'M'
            ret['indi_family']['father_full_name'] = _('Unknown father')
        if mother:
            ret['indi_family']['mother_id'] = mother.get_id()
            ret['indi_family']['mother_sex'] = mother.get_sex()
            ret['indi_family']['mother_full_name'] = mother.get_name()
        else:
            ret['indi_family']['mother_id'] = 0
            ret['indi_family']['mother_sex'] = 'F'
            ret['indi_family']['mother_full_name'] = _('Unknown mother')
        return ret

    def get_context_data(self):
        context = super().get_context_data()
        context['tree_id'] = self.kwargs.get('ft')
        view = self.kwargs.get('view', '')
        indi = IndividualRecord(self.get_object())
        if indi:
            match view:
                case 'life':
                    context['life_info'] = self.get_life_info(indi)
        return context
