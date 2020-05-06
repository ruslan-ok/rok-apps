from datetime import datetime, date, timedelta
from django.utils import timezone

#----------------------------------
def next_period(last = None):
    if not last:
        y = datetime.now().year
        m = datetime.now().month
        if (m == 1):
            m = 12
            y = y - 1
        else:
            m = m - 1
    else:
        y = last.year
        m = last.month
        
        if (m == 12):
            y = y + 1
            m = 1
        else:
            m = m + 1

    return date(y, m, 1)

#----------------------------------
def get_prev_period(period):
    y = period.year
    m = period.month
    if (m == 1):
        m = 12
        y = y - 1
    else:
        m = m - 1
    return date(y, m, 1)


#----------------------------------
def get_new_period():
    dt1 = timezone.now()
    dt2 = dt1.replace(day = 1)
    dt3 = dt2 - timedelta(days = 1)
    dt4 = dt3.replace(day = 1)
    return dt4

