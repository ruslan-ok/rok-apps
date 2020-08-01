from datetime import datetime, date, timezone, timedelta
from django.utils.translation import gettext_lazy as _

# Modes
ALL = 0
MY_DAY = 1
IMPORTANT = 2
PLANNED = 3
COMPLETED = 4
LIST_MODE = 7


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

TERM_NAME = {
    ALL: '',
    LONG_TIME: _('quite a long time ago'), # Совсем давно
    LAST_MONTH: _('last month'), # В прошлом месяце
    THREE_WEEKS: _('three weeks ago'), # Три недели назад
    TWO_WEEKS: _('two weeks ago'), # Две недели назад
    LAST_WEEK: _('last week'), # На прошлой неделе
    MON: _('monday'), # Понедельник
    TUE: _('tuesday'), # Вторник
    WED: _('wednesday'), # Среда
    THU: _('thursday'), # Четверг
    FRI: _('friday'), # Пятница
    SAT: _('saturday'), # Суббота
    SUN: _('sunday'), # Воскресенье
    YESTERDAY: _('yesterday'), # Вчера
    TODAY: _('today'), # Сегодня
    TOMORROW: _('tomorrow'), # Завтра
    THIS_WEEK: _('this week'), # На этой неделе
    NEXT_WEEK: _('next week'), # На следующей неделе
    THIS_MONTH: _('this month'), # В этом месяце
    NEXT_MONTH: _('next month'), # В следующем месяце
    MUCH_LATER: _('later than a month later') # Позже, чем через месяц
}

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

GRP_PLANNED_NONE     = 0
GRP_PLANNED_EARLIER  = 1
GRP_PLANNED_TODAY    = 2
GRP_PLANNED_TOMORROW = 3
GRP_PLANNED_ON_WEEK  = 4
GRP_PLANNED_LATER    = 5
GRP_PLANNED_DONE     = 6

GRPS_PLANNED = {
    GRP_PLANNED_NONE:     '',
    GRP_PLANNED_EARLIER:  _('earlier'),
    GRP_PLANNED_TODAY:    _('today'),
    GRP_PLANNED_TOMORROW: _('tomorrow'),
    GRP_PLANNED_ON_WEEK:  _('on the week'),
    GRP_PLANNED_LATER:    _('later'),
    GRP_PLANNED_DONE:     _('completed'),
}  

def get_grp_planned(view, d, completed):
    if completed and (view in [MY_DAY, LIST_MODE]):
        return GRP_PLANNED_DONE

    if (not d) or (view != PLANNED):
        return GRP_PLANNED_NONE
     
    today = date.today()
    if (d == today):
        return GRP_PLANNED_TODAY

    days = (d - today).days

    if (days == 1):
        return GRP_PLANNED_TOMORROW

    if (days < 0):
        return GRP_PLANNED_EARLIER

    if (days < 8):
        return GRP_PLANNED_ON_WEEK

    return GRP_PLANNED_LATER

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

def get_task_status(task):
    if task.completed:
        if task.completion:
            return str(_('completed:').capitalize()) + nice_date(task.completion.date())
        else:
            return str(_('completed:').capitalize()) + nice_date(task.stop)
    return str(_('created:').capitalize()) + nice_date(task.created.date())

def get_week_day_name(weekday_num):
    d = date(2020, 7, 13)
    if (weekday_num > 1):
        d = d + timedelta(weekday_num - 1)
    return d.strftime('%a')

