import calendar
from datetime import datetime, date

from hier.tree import TreeNode
from hier.models import Folder
from hier.utils import rmtree
from .models import Depart, DepHist, Appoint, Period, Params

def hit_period(pb, ab, ae):

    if (pb == None):
        return True

    # Какое-то левое назначение
    if (ab == None) and (ae == None):
        return True

    last_day = calendar.monthrange(pb.year, pb.month)[1]
    pe = date(pb.year, pb.month, last_day)

    # Назначение начинается в текущем месяце
    if ((ab != None) and (pb <= ab) and (ab <= pe)):
        return True

    # Назначение заканчивается в текущем месяце
    if ((ae != None) and (pb <= ae) and (ae <= pe)):
        return True
  
    # Назначение начинается до текущего месяца, а заканчивается позже
    if ((ab < pb) and ((ae == None) or (pe < ae))):
        return True

    return False

def scan_level(user, folder_node_id, dep_hist_node_id, date, level):
    if (dep_hist_node_id == 0):
        dep_hist_node_id = None

    npp_list = {}
    
    for hist in DepHist.objects.filter(user = user.id, node = dep_hist_node_id):
        if (hist.dBeg > date):
            continue

        nexts = DepHist.objects.filter(user = user.id, depart = hist.depart, dBeg__gt = hist.dBeg).order_by('dBeg')

        next = None
        if nexts:
            next = nexts[0]

        if next:
            if (next.dBeg <= date):
                continue
    
        if (hist.depart):
            npp_list[hist.depart.sort] = hist.depart.id

    keys = list(npp_list.keys())
    keys.sort()

    for npp in keys:
        depart = Depart.objects.get(id = npp_list[npp])
        if (depart == None):
            continue

        dep_folder = Folder.objects.create(user = user,
            node = folder_node_id,
            code = depart.sort,
            name = depart.name,
            creation = datetime.now(),
            last_mod = datetime.now(),
            is_open = depart.is_open,
            icon = 'door-open',
            color = '#004080',
            model_name = 'wage:depart',
            content_id = depart.id,
            is_folder = True)

        for appoint in Appoint.objects.filter(depart = depart):
            if (appoint.dBeg > date):
                continue
        
            if not hit_period(date, appoint.dBeg, appoint.dEnd):
                continue
        
            empl_folder = Folder.objects.create(user = user,
                node = dep_folder.id,
                code = appoint.employee.sort,
                name = appoint.employee.fio,
                creation = datetime.now(),
                last_mod = datetime.now(),
                is_open = False,
                icon = 'user',
                color = '#008080',
                model_name = 'wage:empl',
                content_id = appoint.employee.id,
                is_folder = True)

            add_tab(empl_folder, '10', 'appoint',   'address-card',        'Назначения')
            add_tab(empl_folder, '20', 'empl_per',  'vote-yea',            'Итоги месца')
            add_tab(empl_folder, '30', 'accrual',   'file-invoice-dollar', 'Начисления')
            add_tab(empl_folder, '40', 'payout',    'money-bill-wave',     'Выплаты')
            add_tab(empl_folder, '50', 'education', 'graduation-cap',      'Образование')
            add_tab(empl_folder, '60', 'fio_hist',  'signature',           'Фамилии')
            add_tab(empl_folder, '70', 'child',     'child',               'Дети')

        scan_level(user, dep_folder.id, depart.id, date, level + 1)

def add_tab(empl_folder, sort, model, icon, name):
    Folder.objects.create(user = empl_folder.user,
        node = empl_folder.id,
        code = sort,
        name = name,
        creation = datetime.now(),
        last_mod = datetime.now(),
        is_open = False,
        icon = icon,
        color = '#008080',
        model_name = 'wage:' + model,
        content_id = empl_folder.content_id,
        is_folder = True)


def build_tree(user, date):
        if Folder.objects.filter(user = user.id, node = 0, model_name = 'wage:node').exists():
            node = Folder.objects.filter(user = user.id, node = 0, model_name = 'wage:node').get()
            if Folder.objects.filter(user = user.id, node = node.id, model_name = 'wage:staff').exists():
                staff = Folder.objects.filter(user = user.id, node = node.id, model_name = 'wage:staff').get()
                rmtree(user, staff.id, False)
                scan_level(user, staff.id, 0, date, 2)


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
        if Params.objects.filter(user = user.id).exists():
            par = Params.objects.filter(user = user.id).get()
            par.period = period
            par.save()
        build_tree(user, period.dBeg)

