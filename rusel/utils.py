from django.core.exceptions import FieldError
from datetime import datetime, date
from django.utils.translation import gettext_lazy as _

def extract_get_params(request, group_entity):
    v = request.GET.get('view')
    if not v:
        v = ''
    g = request.GET.get(group_entity)
    if not g:
        g = ''
    q = request.GET.get('q')
    if not q:
        q = ''
    p = request.GET.get('page')
    if not p:
        p = ''
    rt = request.GET.get('ret')
    if not rt:
        rt = ''

    ret = ''
    if v:
        ret += 'view=' + v
    if (not v) and g:
        ret += group_entity + '=' + g
    if q:
        if ret:
            ret += '&'
        ret += 'q=' + q
    if p:
        if ret:
            ret += '&'
        ret += 'page=' + p
    if rt:
        if ret:
            ret += '&'
        ret += 'ret=' + rt
    
    if ret:
        ret = '?' + ret
    return ret


LONG_TIME = 20 # Совсем давно
LAST_MONTH = 19 # В прошлом месяце
THREE_WEEKS = 18 # Три недели назад
TWO_WEEKS = 17 # Две недели назад
LAST_WEEK = 16 # На прошлой неделе
MON = 15 # Понедельник
TUE = 14 # Вторник
WED = 13 # Среда
THU = 12 # Четверг
FRI = 11 # Пятница
SAT = 10 # Суббота
SUN = 9 # Воскресенье
YESTERDAY = 8 # Вчера
TODAY = 7 # Сегодня
TOMORROW = 6 # Завтра
THIS_WEEK = 5 # На этой неделе
NEXT_WEEK = 4 # На следующей неделе
THIS_MONTH = 3 # В этом месяце
NEXT_MONTH = 2 # В следующем месяце
MUCH_LATER = 1 # Позже, чем через месяц
ALL = 0 # Все сроки


def get_term_from_today(next):
    if not next:
        return ALL

    today = date.today()

    match next:
        case datetime():
            next_date = next.date()
        case date():
            next_date = next

    days = (next_date - today).days

    if (days == 0):
        return TODAY

    if (days == 1):
        return TOMORROW

    if (days == -1):
        return YESTERDAY

    weeks = next_date.isocalendar()[1] - today.isocalendar()[1]
    if (weeks == 0):
        if (days > 0):
            return THIS_WEEK
        if (next_date.weekday() == 0):
            return MON
        if (next_date.weekday() == 1):
            return TUE
        if (next_date.weekday() == 2):
            return WED
        if (next_date.weekday() == 3):
            return THU
        if (next_date.weekday() == 4):
            return FRI
        if (next_date.weekday() == 5):
            return SAT
        if (next_date.weekday() == 6):
            return SUN
    if (weeks == 1):
        return NEXT_WEEK
    if (weeks == -1):
        return LAST_WEEK

    months = (next_date.year - today.year) * 12 + next_date.month - today.month
    if (weeks == -2) and (months == 0):
        return TWO_WEEKS
    if (weeks == -3) and (months == 0):
        return THREE_WEEKS

    if (months == 0):
        return THIS_MONTH
    if (months == 1):
        return NEXT_MONTH
    if (months > 1):
        return MUCH_LATER
    if (months == -1):
        return LAST_MONTH

    return LONG_TIME

def only_nice_date(d):

    if not d:
        return ''
    
    term = get_term_from_today(d)
    ret = ''

    if (term == TODAY):
        ret = str(_('today')).capitalize()
    
    if (term == TOMORROW):
        ret = str(_('tomorrow')).capitalize()
    
    if (term == YESTERDAY):
        ret = str(_('yesterday')).capitalize()

    match d:
        case datetime() if ret and (d.strftime('%H:%M') != '00:00'):
            ret += d.strftime(' %H:%M')

    return ret


def nice_date(d):

    ret = only_nice_date(d)
    if (ret != ''):
        return ret
    
    match d:
        case date():
            if (d.year == date.today().year):
                return d.strftime('%a, %d %b')
            else:
                return d.strftime('%a, %d %b %Y')
        case datetime() if d.minute == 0 and d.hour == 0:
            if (d.year == date.today().year):
                return d.strftime('%a, %d %b')
            else:
                return d.strftime('%a, %d %b %Y')
        case datetime():
            if (d.year == date.today().year):
                return d.strftime('%a, %d %b %H:%M')
            else:
                return d.strftime('%a, %d %b %Y %H:%M')
        case _:
            return ''

def sort_data(data, sort, reverse):
    if not data:
        return data

    sort_fields = sort.split()
    if reverse:
        revers_list = []
        for sf in sort_fields:
            if (sf[0] == '-'):
                revers_list.append(sf[1:])
            else:
                revers_list.append('-' + sf)
        sort_fields = revers_list

    #raise Exception(sort, reverse, sort_fields)
    try:
        if (len(sort_fields) == 1):
            data = data.order_by(sort_fields[0])
        elif (len(sort_fields) == 2):
            data = data.order_by(sort_fields[0], sort_fields[1])
        elif (len(sort_fields) == 3):
            data = data.order_by(sort_fields[0], sort_fields[1], sort_fields[2])
    except FieldError:
        pass
    
    return data

def get_search_mode(query):
    if not query:
        return 0
    if (len(query) > 1) and (query[0] == '@') and (query.find(' ') == -1):
        return 2
    else:
        return 1
