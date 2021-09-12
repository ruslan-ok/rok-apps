from datetime import datetime, date, timezone, timedelta
from django.utils.translation import gettext_lazy as _

def extract_get_params(request):
    v = request.GET.get('view')
    if not v:
        v = ''
    g = request.GET.get('group_id')
    if not g:
        g = ''
    q = request.GET.get('q')
    if not q:
        q = ''
    p = request.GET.get('page')
    if not p:
        p = ''
    ret = ''
    if v:
        ret += 'view=' + v
    if (v == 'group') and g:
        ret += '&group_id=' + g
    if q:
        if ret:
            ret += '&'
        ret += 'q=' + q
    if p:
        if ret:
            ret += '&'
        ret += 'page=' + p
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


def get_term_for_two_dates(today, next):
    if not next:
        return ALL
    
    if (next == today):
        return TODAY

    days = (next - today).days
    if (days == 1):
        return TOMORROW
    if (days == -1):
        return YESTERDAY

    weeks = next.isocalendar()[1] - today.isocalendar()[1]
    if (weeks == 0):
        if (days > 0):
            return THIS_WEEK
        if (next.weekday() == 0):
            return MON
        if (next.weekday() == 1):
            return TUE
        if (next.weekday() == 2):
            return WED
        if (next.weekday() == 3):
            return THU
        if (next.weekday() == 4):
            return FRI
        if (next.weekday() == 5):
            return SAT
        if (next.weekday() == 6):
            return SUN
    if (weeks == 1):
        return NEXT_WEEK
    if (weeks == -1):
        return LAST_WEEK

    months = (next.year - today.year) * 12 + next.month - today.month
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
    
    term = get_term_for_two_dates(date.today(), d)

    if (term == TODAY):
        return str(_('today')).capitalize()
    
    if (term == TOMORROW):
        return str(_('tomorrow')).capitalize()
    
    if (term == YESTERDAY):
        return str(_('yesterday')).capitalize()

    return ''


def nice_date(d):

    ret = only_nice_date(d)
    if (ret != ''):
        return ret
    
    if (d.year == date.today().year):
        return d.strftime('%a, %d %B')
    else:
        return d.strftime('%a, %d %B %Y')


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
