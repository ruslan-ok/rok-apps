import math
from django.utils.translation import gettext_lazy as _, to_locale, get_language, pgettext

ADPM = 30.42 # average days per month
LANG_EN = 0
LANG_AUTO = 1
LANG_RU = 2

def declination(num, singular, plural, tr_singular, tr_plural_2_4, tr_plural_5_10, lang=LANG_AUTO):
    if (lang == LANG_AUTO and to_locale(get_language()) == 'en'):
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

def day_declination(value, lang=LANG_AUTO):
    if lang == LANG_AUTO:
        lbl_singular = _('day')
        lbl_plural_2_4 = pgettext('2-4', 'days')
        lbl_plural_5_10 = pgettext('5-10', 'days')
    elif lang == LANG_RU:
        lbl_singular = 'день'
        lbl_plural_2_4 = 'дня'
        lbl_plural_5_10 = 'дней'
    else:
        lbl_singular = 'day'
        lbl_plural_2_4 = 'days'
        lbl_plural_5_10 = 'days'

    s_days = declination(value, 'day', 'days', lbl_singular, lbl_plural_2_4, lbl_plural_5_10, lang)
    return '{} {}'.format(value, s_days)

def month_declination(value, lang=LANG_AUTO):
    if lang == LANG_AUTO:
        lbl_singular = _('month')
        lbl_plural_2_4 = pgettext('2-4', 'months')
        lbl_plural_5_10 = pgettext('5-10', 'months')
    elif lang == LANG_RU:
        lbl_singular = 'месяц'
        lbl_plural_2_4 = 'месяца'
        lbl_plural_5_10 = 'месяцев'
    else:
        lbl_singular = 'month'
        lbl_plural_2_4 = 'months'
        lbl_plural_5_10 = 'months'

    s_months = declination(value, 'month', 'months', lbl_singular, lbl_plural_2_4, lbl_plural_5_10, lang)
    return '{} {}'.format(value, s_months)

def year_declination(value, lang=LANG_AUTO):
    if lang == LANG_AUTO:
        lbl_singular = _('year')
        lbl_plural_2_4 = pgettext('2-4', 'years')
        lbl_plural_5_10 = pgettext('5-10', 'years')
    elif lang == LANG_RU:
        lbl_singular = ''
        lbl_plural_2_4 = ''
        lbl_plural_5_10 = ''
    else:
        lbl_singular = ''
        lbl_plural_2_4 = ''
        lbl_plural_5_10 = ''

    years = math.floor(value / 12)
    months = round(value % 12)
    s_years = declination(years, 'year', 'years', lbl_singular, lbl_plural_2_4, lbl_plural_5_10, lang)
    s_years = '{} {}'.format(years, s_years)
    s_months = ''
    if months:
        s_months = ' {} {}'.format(_('and'), month_declination(months), lang)
    return s_years + s_months

def get_rest(item, last_odo, last_repl, lang=LANG_AUTO):
    if ((not item.part_chg_km) and (not item.part_chg_mo)) or (not last_odo):
        return None

    output = ''
    p1 = ''
    p2 = ''
    m1 = False
    m2 = False
    color = 'normal'

    if lang == LANG_AUTO:
        lbl_km = _('km')
        lbl_thsd_km = _('thsd km')
        lbl_overdue = _('overdue')
        lbl_or = _('or')
        lbl_left_pre = ''
        lbl_left_post = ''
    elif lang == LANG_RU:
        lbl_km = 'км'
        lbl_thsd_km = 'тыс км'
        lbl_overdue = 'просрочено'
        lbl_or = 'или'
        lbl_left_pre = 'осталось '
        lbl_left_post = ''
    else:
        lbl_km = 'km'
        lbl_thsd_km = 'thsd km'
        lbl_overdue = 'overdue'
        lbl_or = 'or'
        lbl_left_pre = ''
        lbl_left_post = ' left'

    if item.part_chg_km:
        trip_km_unround = last_odo.car_odometr - last_repl.car_odometr # How many kilometers have traveled since the last change
        
        trip_km = trip_km_unround
        if (trip_km > 1000):
            trip_km = round(trip_km_unround / 1000) * 1000
        
        if (trip_km_unround > item.part_chg_km):
            if ((trip_km_unround - item.part_chg_km) >= 1000):
                p1 = '{} {} {}'.format(round((trip_km_unround - item.part_chg_km) / 1000), lbl_thsd_km, lbl_overdue)
            else:
                p1 = '{} {} {}'.format(trip_km_unround - item.part_chg_km, lbl_km, lbl_overdue)
            color = 'error'
            m1 = True
        else:
            if ((item.part_chg_km - trip_km_unround) < 1000):
                p1 = '{}{} {}{}'.format(lbl_left_pre, item.part_chg_km - trip_km_unround, lbl_km, lbl_left_post)
                color = 'warning'
            else:
                p1 = '{} {}'.format(round((item.part_chg_km - trip_km) / 1000), lbl_thsd_km)
            
    if (item.part_chg_mo):
        trip_days = (last_odo.event.date() - last_repl.event.date()).days - item.part_chg_mo * ADPM
        per = ''
        days = trip_days
        if (days < 0):
            days = -1 * days
        
        if (days >= 365):
            per = year_declination(round(days/ADPM), lang)
        elif (days >= ADPM):
            per = month_declination(round(days/ADPM), lang)
        else:
            per = day_declination(round(days), lang)
        
        if (trip_days > 0):
            p2 = '{} {}'.format(per, lbl_overdue)
            m2 = True
            color = 'error'
        else:
            if (days < 32):
                p2 = '{}{}{}'.format(lbl_left_pre, per, lbl_left_post)
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
        output = '{} {} {}'.format(p1, lbl_or, p2)

    return output, 'rest-color-' + color
