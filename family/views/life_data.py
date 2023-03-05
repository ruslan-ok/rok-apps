from dataclasses import dataclass, field
from django.utils.translation import gettext_lazy as _
from family.models import IndividualRecord, IndividualEventStructure, FamilyEventStructure, FamRecord
from family.views.life_date import EventDate
from family.descriptions.individual import DescriptorIndi
from family.descriptions.event import DescriptorEvent

@dataclass
class PersonInfo:
    id: int = field(init=False)
    role: str = field(init=False)
    sex: str = field(init=False)
    name: str = field(init=False)
    given_name: str = field(init=False)
    img_href: str = field(init=False)
    live_time: str = field(init=False)

    def __init__(self, role, indi: IndividualRecord | None):
        self.role = role
        if indi:
            self.id = indi.get_id()
            self.sex = indi.get_sex()
            self.name = indi.get_name()
            self.given_name = indi.get_name('given')
            self.img_href = indi.get_photo_url()
            birth = indi.get_event('BIRT')
            death = indi.get_event('DEAT')
            bd = dd = ''
            if birth and birth.deta and birth.deta.date:
                obd = EventDate(birth.deta.date)
                bd = obd.year
            if death and death.deta and death.deta.date:
                odd = EventDate(death.deta.date)
                dd = odd.year
            self.live_time = bd + '-' + dd
        else:
            self.id = 0
            self.sex = ''
            self.name = ''
            self.given_name = ''
            self.img_href = ''
            self.live_time = ''

@dataclass
class GeoInfo:
    lat: float | None
    lon: float | None

@dataclass
class EventInfo:
    id: int = field(init=False)
    tag: str = field(init=False)
    title: str = field(init=False)
    is_last: bool = field(init=False)
    is_editable: bool = field(init=False)
    date: EventDate = field(init=False)
    place: str = field(init=False)
    age: int | None = field(init=False)
    indi: PersonInfo | None = field(init=False)
    geo: GeoInfo = field(init=False)
    descr: str = field(init=False)

@dataclass
class IndiEventInfo(EventInfo):
    def __init__(self, role: str, indi: IndividualRecord, event: IndividualEventStructure):
        self.id = event.id
        self.tag = event.tag if event.tag else ''
        raw_date = ''
        if event.deta:
            raw_date = event.deta.date
        self.date = EventDate(raw_date, self.tag)
        self.place = ''
        if event.deta and event.deta.plac and event.deta.plac.name:
            self.place = event.deta.plac.name
        relative = event.indi
        relative_sex = relative.get_sex()
        if not relative_sex:
            relative_sex = 'M'
        describer = DescriptorEvent(self.tag, self.date, self.place, indi, relative, role)
        self.title = describer.get_event_title()
        self.descr = describer.get_event_descr()
        if role != 'indi' or (self.tag != 'BIRT' and self.tag != 'DEAT'):
            self.indi = PersonInfo(role, relative)
        else:
            self.indi = None
        lat = lon = None
        if event.deta and event.deta.plac and event.deta.plac.map_lati and event.deta.plac.map_long:
            lat = float(event.deta.plac.map_lati)
            lon = float(event.deta.plac.map_long)
        self.geo = GeoInfo(lat, lon)
        self.is_editable = role == 'indi'
        self.is_last = False

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

@dataclass
class FamEventInfo(EventInfo):
    fam: FamRecord

    def __init__(self, indi: IndividualRecord, spouse: IndividualRecord, event: FamilyEventStructure):
        self.id = event.id
        self.fam = event.fam
        self.tag = event.tag if event.tag else ''
        raw_date = ''
        if event.deta:
            raw_date = event.deta.date
        self.date = EventDate(raw_date, self.tag)
        self.place = ''
        if event.deta and event.deta.plac and event.deta.plac.name:
            self.place = event.deta.plac.name
        describer = DescriptorEvent(self.tag, self.date, self.place, indi, spouse, 'spouse')
        describer.fam = event.fam
        self.title = describer.get_event_title()
        self.descr = describer.get_event_descr()
        self.indi = PersonInfo('spouse', spouse)
        lat = lon = None
        if event.deta and event.deta.plac and event.deta.plac.map_lati and event.deta.plac.map_long:
            lat = float(event.deta.plac.map_lati)
            lon = float(event.deta.plac.map_long)
        self.geo = GeoInfo(lat, lon)
        self.is_editable = True
        self.is_last = False

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

@dataclass
class MapPointInfo:
    id: int
    name: str
    date: str
    place: str
    lat: float
    lon: float

@dataclass
class LifeInfo:
    biography: str = field(init=False)
    indi: PersonInfo = field(init=False)
    father: PersonInfo = field(init=False)
    mother: PersonInfo = field(init=False)
    children: list[PersonInfo] = field(default_factory=list)
    spouses: list[PersonInfo] = field(default_factory=list)
    events: list[EventInfo] = field(default_factory=list)
    map_points: list[MapPointInfo] = field(default_factory=list)

    def __init__(self, indi: IndividualRecord):
        describer = DescriptorIndi(indi)
        biography = describer.get_biography()
        self.biography = biography
        father, mother = indi.get_parents()
        self.indi = PersonInfo('indi', indi)
        self.father = PersonInfo('father', father)
        self.mother = PersonInfo('mother', mother)

        indi_list = []
        indi_list.append(self.indi)
        indi_list.append(self.father)
        indi_list.append(self.mother)
        self.spouses = []
        for spouse in indi.get_spouses():
            si = PersonInfo('spouse', spouse)
            self.spouses.append(si)
            indi_list.append(si)
        self.children = []
        for child in indi.get_children():
            ci = PersonInfo('child', child)
            self.children.append(ci)
            indi_list.append(ci)

        bd = dd = ''
        events_all = []
        for x in indi_list:
            if not x.id:
                continue
            ir = IndividualRecord.objects.get(id=x.id)
            for event in ir.get_events():
                if x.role == 'spouse' and event.tag != 'DEAT':
                    continue
                ev = IndiEventInfo(x.role, indi, event)
                if ev.date.str_date:
                    ev.age = indi.get_age(ev.date.str_date, bd)
                    events_all.append(ev)
                    match x.role, ev.tag:
                        case 'indi', 'BIRT': 
                                bd = ev.date.str_date
                        case 'indi', 'DEAT': 
                                dd = ev.date.str_date

        for fam in indi.get_families():
            for event in fam.get_events():
                spouse = fam.get_spouse(indi)
                if spouse:
                    ev = FamEventInfo(indi, spouse, event)
                    if ev.date.str_date:
                        ev.age = indi.get_age(ev.date.str_date, bd)
                        events_all.append(ev)

        # Filter and sort events
        events = []
        self.map_points = []
        for x in events_all:
            if (x.tag != 'BURI') and (not bd or x.date.sort >= bd) and (not dd or x.date.sort <= dd):
                events.append(x)
                # Map points
                if x.geo and x.geo.lat and x.geo.lon:
                    name = x.title
                    if x.indi:
                        name += ' ' + x.indi.given_name
                    self.map_points.append(MapPointInfo(
                        id=x.id,
                        name=name,
                        date=x.date.when,
                        place=x.place,
                        lat=x.geo.lat,
                        lon=x.geo.lon
                    ))
        self.events = sorted(events, key=lambda x: x.date.sort)
        self.events[-1].is_last = True
