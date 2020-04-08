import calendar
from .models import Depart, DepHist, Appoint
from datetime import datetime, date

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

class TreeNode():
    is_depart = True
    id = 0
    parent = 0
    name = ''
    indent = ''
    is_open = False

    def __init__(self, is_depart, id, parent, name, indent, is_open = False):
        self.is_depart = is_depart
        self.id = id
        self.parent = parent
        self.name = name
        self.indent = indent
        self.is_open = is_open


def scan_level(tree, user, node, date, level):
    if (node == 0):
        node = None

    npp_list = {}
    
    for hist in DepHist.objects.filter(user = user, node = node):
        if (hist.dBeg > date):
            continue

        nexts = DepHist.objects.filter(user = user, depart = hist.depart, dBeg__gt = hist.dBeg).order_by('dBeg')

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

        tree.append(TreeNode(True, depart.id, node, depart.name, '.' * (level * 6), depart.is_open))

        if depart.is_open:
            for appoint in Appoint.objects.filter(depart = depart):
                if (appoint.dBeg > date):
                    continue
        
                if not hit_period(date, appoint.dBeg, appoint.dEnd):
                    continue
        
                tree.append(TreeNode(False, appoint.employee.id, node, appoint.employee.fio, '.' * ((level + 1) * 6)))

        if depart.is_open:
            scan_level(tree, user, depart.id, date, level + 1)


def build_tree(user, node, date):
    tree = []
    scan_level(tree, user, node, date, 0)
    return tree


