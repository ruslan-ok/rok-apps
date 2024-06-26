from datetime import datetime
from dataclasses import dataclass, field
from django.utils.formats import date_format
from django.utils.translation import pgettext_lazy
from family.ged4py.date import DateValue


@dataclass
class EventDate:
    raw: str
    str_date: str = field(init=False)
    full: str = field(init=False)
    when: str = field(init=False)
    sort: str = field(init=False)
    day_month: str = field(init=False)
    year: str = field(init=False)

    def __init__(self, raw=None, tag: str=''):
        self.full = self.when = self.sort = self.day_month = self.year = self.str_date = ''
        if not raw:
            self.raw = ''
            return
        self.raw = raw
        ev_date = DateValue.parse(raw)
        if ev_date:
            self.str_date = ev_date.get_str_date()
        self.full = self.day_month = self.year = ''
        try:
            dt = datetime.strptime(self.str_date, '%Y-%m-%d')
            self.full = date_format(dt, format='DATE_FORMAT', use_l10n=True)
            self.day_month = dt.strftime('%d %b')
            self.year = dt.strftime('%Y')
        except:
            try:
                self.year = str(int(self.str_date))
                self.full = self.year
            except:
                pass
        self.when = ''
        if self.day_month:
            self.when = pgettext_lazy('event date', 'on %(date)s') % {'date': self.full}
        elif self.year:
            self.when = pgettext_lazy('event date', 'in %(date)s') % {'date': self.year}
        match tag:
            case 'DEAT': extra = '1'
            case 'BURI': extra = '2'
            case _: extra = '0'
        self.sort = self.str_date + '-ex-' + extra

    def __repr__(self):
        return type(self).__name__ + '(' + self.str_date + ')'

