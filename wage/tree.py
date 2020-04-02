"""
private procedure ScanDepHist(_src: byte; _dst: comp);
{
  PushPos(tnmtDepHist);
  _loop mtDepHist where (( _src           == mtDepHist.Node and
                           mtPeriod.dBeg >>= mtDepHist.dBeg ))
  {
    if ((mtDepHist.dEnd <> ZeroDate) and (mtDepHist.dEnd < mtPeriod.dBeg))
      continue;

    if (GetFirst mtDepart where (( mtDepHist.Depart == mtDepart.Id )) <> tsOk)
      continue;

    insert mtStruct set mtStruct.Period := mtPeriod.Id,
                        mtStruct.Node   := _dst,
                        mtStruct.Mode   := 1,
                        mtStruct.Depart := mtDepHist.Depart,
                        mtStruct.Name   := mtDepart.Name,
                        mtStruct.Sort   := string(mtDepart.Sort);
    ScanAppoint(mtDepHist.Depart, mtStruct.NRec);
    ScanDepHist(mtDepHist.Depart, mtStruct.NRec);
  }
  PopPos(tnmtDepHist);
}


private procedure ScanAppoint(_dep: byte; _dst: comp);
{
  PushPos(tnmtAppoint);
  PushPos(tnmtStruct);

  _loop mtAppoint where (( _dep == mtAppoint.Depart and
                 mtPeriod.dEnd >>= mtAppoint.dBeg ))
  {
    if (not isHitPeriod)
      continue;

    if (GetFirst mtPerson where (( mtAppoint.Person == mtPerson.Id )) <> tsOk)
      continue;

    var sFIO: string;
    if (GetLast mtFioHist where (( mtPerson.Id    == mtFioHist.Person and
                                   mtPeriod.dBeg <<= mtFioHist.dEnd )) = tsOk)
      sFIO := mtFioHist.FIO;
    else
      sFIO := mtPerson.FIO;

    if (GetFirst mtStruct where (( mtPeriod.Id == mtStruct.Period and
                                          _dst == mtStruct.Node   and
                                             2 == mtStruct.Mode   and
                              mtAppoint.Person == mtStruct.Person )) <> tsOk)
      insert mtStruct set mtStruct.Period := mtPeriod.Id,
                          mtStruct.Node   := _dst,
                          mtStruct.Mode   := 2,
                          mtStruct.Person := mtAppoint.Person,
                          mtStruct.Name   := sFIO,
                          mtStruct.Sort   := LPadCh(string(mtPerson.Sort), '0', 6);

  }
  PopPos(tnmtStruct);
  PopPos(tnmtAppoint);
}
private function isHitPeriod: boolean;
{
  result := true;

  if (mtPeriod.dBeg = ZeroDate)
    exit;

  if ((mtAppoint.dBeg = ZeroDate) and (mtAppoint.dEnd = ZeroDate))
    exit; // Какое-то левое назначение

  // Назначение начинается в текущем месяце
  if ((mtAppoint.dBeg <> ZeroDate) and (mtPeriod.dBeg <= mtAppoint.dBeg) and (mtAppoint.dBeg <= mtPeriod.dEnd))
    exit;

  // Назначение заканчивается в текущем месяце
  if ((mtAppoint.dEnd <> ZeroDate) and (mtPeriod.dBeg <= mtAppoint.dEnd) and (mtAppoint.dEnd <= mtPeriod.dEnd))
    exit;

  // Назначение начинается до текущего месяца, а заканчивается позже
  if ((mtAppoint.dBeg < mtPeriod.dBeg) and ((mtAppoint.dEnd = ZeroDate) or (mtPeriod.dEnd < mtAppoint.dEnd)))
    exit;

  result := false;
}

"""
import calendar
from .models import Depart, DepHist, Appoint
from datetime import datetime, date

def isHitPeriod(pb, ab, ae):

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
    is_visible = True
    name = ''
    indent = ''
    is_open = False

    def __init__(self, is_depart, id, parent, is_visible, name, indent, is_open = False):
        self.is_depart = is_depart
        self.id = id
        self.parent = parent
        self.is_visible = is_visible
        self.name = name
        self.indent = indent
        self.is_open = is_open


def ScanLevel(tree, user, node, date, level, vis):
    if (node == 0):
        node = None

    npp_list = {}
    
    for hist in DepHist.objects.filter(user = user, node = node):
        if (hist.dBeg > date) or ((hist.dEnd != None) and (hist.dEnd < date)):
            continue
    
        npp_list[hist.depart.sort] = hist.depart.id

    keys = list(npp_list.keys())
    keys.sort()

    for npp in keys:
        depart = Depart.objects.get(id = npp_list[npp])
        if (depart == None):
            continue

        tree.append(TreeNode(True, depart.id, node, vis, depart.name, '.' * (level * 6), depart.is_open))

        if depart.is_open:
            for appoint in Appoint.objects.filter(depart = depart):
                if (appoint.dBeg > date):
                    continue
        
                if not isHitPeriod(date, appoint.dBeg, appoint.dEnd):
                    continue
        
                tree.append(TreeNode(False, appoint.employee.id, node, vis, appoint.employee.fio, '.' * ((level + 1) * 6)))

        if depart.is_open:
            ScanLevel(tree, user, depart.id, date, level + 1, True)


def BuildTree(user, node, date):
    tree = []
    ScanLevel(tree, user, node, date, 0, True)
    return tree


def ToggleTreeNode(tree, pk):
    cur_visible = True
    for node in tree:
        if (node.is_depart) and (node.id == pk):
            node.is_open = not node.is_open
            cur_visible = node.is_open
        if (node.parent == pk):
            node.is_visible = cur_visible

