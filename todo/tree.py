from .models import Task, Grp, Lst

class TreeNode():
    id = 0
    parent = 0
    name = ''
    level = 0
    is_list = False
    is_open = False
    qty = 0

    def __init__(self, id, parent, name, level, is_list = False, is_open = False, qty = 0):
        self.id = id
        self.parent = parent
        self.name = name
        self.level = level
        self.is_list = is_list
        self.is_open = is_open
        self.qty = qty

    def __str__(self):
        ret = str(self.level) + ' - ' + str(self.parent) + '/' + str(self.id) + ' "' + self.name + '" '
        if self.is_node:
            if self.is_open:
                ret = ret + '[-]'
            else:
                ret = ret + '[+]'
        return ret


def scan_level(tree, user_id, node_id, level, app_name):
    if (node_id == 0):
        node_id = None
    for grp in Grp.objects.filter(user = user_id, app = app_name, node = node_id).order_by('sort', 'name'):
        tree.append(TreeNode(grp.id, node_id, grp.name, level, False, grp.is_open))
        if grp.is_open:
            for lst in Lst.objects.filter(user = user_id, grp = grp.id).order_by('sort', 'name'):
                if (app_name == 'todo'):
                    qty = len(Task.objects.filter(lst = lst.id).exclude(completed = True))
                else:
                    qty = 0
                tree.append(TreeNode(lst.id, grp.id, lst.name, level + 1, True, False, qty))
            scan_level(tree, user_id, grp.id, level + 1, app_name)


def build_tree(user_id, app_name):
    tree = []
    scan_level(tree, user_id, 0, 0, app_name)
    for lst in Lst.objects.filter(user = user_id, grp = None, app = app_name).order_by('sort', 'name'):
        if (app_name == 'todo'):
            qty = len(Task.objects.filter(lst = lst.id).exclude(completed = True))
        else:
            qty = 0
        tree.append(TreeNode(lst.id, 0, lst.name, 0, True, False, qty))
    return tree


