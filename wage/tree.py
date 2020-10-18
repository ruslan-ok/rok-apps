import calendar
from datetime import datetime, date

from hier.models import Folder
from hier.utils import rmtree
from .models import Depart, DepHist, Appoint, Period

def deactivate_all(user_id, period_id):
    for period in Period.objects.filter(user = user_id, active = True).exclude(id = period_id):
        period.active = False
        period.save()

def set_active(user, period_id):
    if Period.objects.filter(user = user.id, id = period_id).exists():
        period = Period.objects.filter(user = user.id, id = period_id).get()
        deactivate_all(user.id, period.id)
        period.active = True
        period.save()
        build_tree(user, period.dBeg)

