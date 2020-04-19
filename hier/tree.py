import calendar
from datetime import datetime, date
from hier.models import File

class TreeNode():
    id = 0
    parent = 0
    name = ''
    level = 0
    is_node = False
    is_open = False
    icon = ''

    def __init__(self, id, parent, name, level, is_node = False, is_open = False, icon = ''):
        self.id = id
        self.parent = parent
        self.name = name
        self.level = level
        self.is_node = is_node
        self.is_open = is_open
        self.icon = icon

    def __str__(self):
        ret = str(self.level) + ' - ' + str(self.parent) + '/' + str(self.id) + ' "' + self.name + '" '
        if self.is_node:
            if self.is_open:
                ret = ret + '[-]'
            else:
                ret = ret + '[+]'
        return ret


def get_is_node(file_id):
    return File.objects.filter(node = file_id).exists()

def scan_level(tree, user_id, node_id, level):
    for file in File.objects.filter(user = user_id, node = node_id).order_by('code', 'name'):
        tree.append(TreeNode(file.id, node_id, file.name, level, get_is_node(file.id), file.is_open, file.icon))

        if file.is_open:
            scan_level(tree, user_id, file.id, level + 1)


def build_tree(user_id, node_id):
    tree = []
    scan_level(tree, user_id, node_id, 0)
    return tree


