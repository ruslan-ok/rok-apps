from datetime import datetime, date, timezone, timedelta
from django.utils.translation import gettext_lazy as _

def extract_get_params(request):
    v = request.GET.get('view')
    if not v:
        v = ''
    l = request.GET.get('lst')
    if not l:
        l = ''
    q = request.GET.get('q')
    if not q:
        q = ''
    p = request.GET.get('page')
    if not p:
        p = ''
    ret = ''
    if v and l:
        ret += 'view={}&lst={}'.format(v, l)
    if q:
        if ret:
            ret += '&'
        ret += 'q={}'.format(q)
    if p:
        if ret:
            ret += '&'
        ret += 'page={}'.format(p)
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


