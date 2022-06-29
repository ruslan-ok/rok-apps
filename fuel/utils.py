import math
from django.utils.translation import gettext_lazy as _, to_locale, get_language, pgettext

ADPM = 30.42 # average days per month

def declination(num, singular, plural, tr_singular, tr_plural_2_4, tr_plural_5_10):
    if (to_locale(get_language()) == 'en'):
        if (num == 1):
            return singular
        else:
            return plural
    else:
        if (num >= 11) and (num <= 14):
            return tr_plural_5_10
        elif ((num % 10) == 1):
            return tr_singular
        elif ((num % 10) >= 2) and ((num % 10) <= 4):
            return tr_plural_2_4
        else:
            return tr_plural_5_10

def day_declination(value):
    s_days = declination(value, 'day', 'days', _('day'), pgettext('2-4', 'days'), pgettext('5-10', 'days'))
    return '{} {}'.format(value, s_days)

def month_declination(value):
    s_months = declination(value, 'month', 'months', _('month'), pgettext('2-4', 'months'), pgettext('5-10', 'months'))
    return '{} {}'.format(value, s_months)

def year_declination(value):
    years = math.floor(value / 12)
    months = round(value % 12)
    s_years = declination(years, 'year', 'years', _('year'), pgettext('2-4', 'years'), pgettext('5-10', 'years'))
    s_years = '{} {}'.format(years, s_years)
    s_months = ''
    if months:
        s_months = ' {} {}'.format(_('and'), month_declination(months))
    return s_years + s_months

def get_rest(item, last_odo, last_repl):
    if ((not item.part_chg_km) and (not item.part_chg_mo)) or (not last_odo):
        return None

    output = ''
    p1 = ''
    p2 = ''
    m1 = False
    m2 = False
    color = 'normal'

    if item.part_chg_km:
        trip_km_unround = last_odo.car_odometr - last_repl.car_odometr # How many kilometers have traveled since the last change
        
        trip_km = trip_km_unround
        if (trip_km > 1000):
            trip_km = round(trip_km_unround / 1000) * 1000
        
        if (trip_km_unround > item.part_chg_km):
            if ((trip_km_unround - item.part_chg_km) >= 1000):
                p1 = '{} {} {}'.format(round((trip_km_unround - item.part_chg_km) / 1000), _('thsd km'), _('overdue'))
            else:
                p1 = '{} {} {}'.format(trip_km_unround - item.part_chg_km, _('km'), _('overdue'))
            color = 'error'
            m1 = True
        else:
            if ((item.part_chg_km - trip_km_unround) < 1000):
                p1 = '{} {}'.format(item.part_chg_km - trip_km_unround, _('km'))
                color = 'warning'
            else:
                p1 = '{} {}'.format(round((item.part_chg_km - trip_km) / 1000), _('thsd km'))
            
    if (item.part_chg_mo):
        trip_days = (last_odo.event.date() - last_repl.event.date()).days - item.part_chg_mo * ADPM
        per = ''
        days = trip_days
        if (days < 0):
            days = -1 * days
        
        if (days >= 365):
            per = year_declination(round(days/ADPM))
        elif (days >= ADPM):
            per = month_declination(round(days/ADPM))
        else:
            per = day_declination(round(days))
        
        if (trip_days > 0):
            p2 = '{} {}'.format(per, _('overdue'))
            m2 = True
            color = 'error'
        else:
            if (days < 32):
                p2 = per
                color = 'warning'
            else:
                p2 = per
    
    if m1:
        output = p1
    elif m2:
        output = p2
    elif (p1 == ''):
        output = p2
    elif (p2 == ''):
        output = p1
    else:
        output = '{} {} {}'.format(p1, _('or'), p2)

    return output, 'rest-color-' + color
