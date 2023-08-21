from django.utils.translation import pgettext_lazy, gettext_lazy as _
from task.const import ROLE_FUEL, ROLE_APP

role = ROLE_FUEL
app = ROLE_APP[role]

def get_info(item):
    attr = []
    attr.append({'text': '{}: {:,}'.format(_('odometr'), item.car_odometr)})
    attr.append({'text': '{}: {:.2f} {}'.format(pgettext_lazy('fuel...', 'volume'), item.fuel_volume, _('l'))})
    attr.append({'text': '{} / {} {}: {:.2f} / {:.0f}'.format(_('price'), _('summa'), item.price_unit, item.fuel_price, item.fuel_volume * item.fuel_price)})
    if item.fuel_volume and item.fuel_price and item.expen_rate_usd:
        usd_prc = item.fuel_price / item.expen_rate_usd
        usd_sum = item.fuel_volume * usd_prc
        attr.append({'text': 'USD: {:.2f} / {:.0f}'.format(usd_prc, usd_sum)})
    item.actualize_role_info(app, role, attr)

