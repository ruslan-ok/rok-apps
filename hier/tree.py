import calendar
from datetime import datetime, date
from hier.models import Folder

class TreeNode():
    id = 0
    parent = 0
    name = ''
    level = 0
    is_node = False
    is_open = False
    icon = ''
    color = ''
    model_name = ''

    def __init__(self, id, parent, name, level, is_node = False, is_open = False, icon = '', color = '', model_name = ''):
        self.id = id
        self.parent = parent
        self.name = name
        self.level = level
        self.is_node = is_node
        self.is_open = is_open
        self.icon = icon
        self.color = color
        model_name = model_name

    def __str__(self):
        ret = str(self.level) + ' - ' + str(self.parent) + '/' + str(self.id) + ' "' + self.name + '" '
        if self.is_node:
            if self.is_open:
                ret = ret + '[-]'
            else:
                ret = ret + '[+]'
        return ret


def get_is_node(folder_id):
    return Folder.objects.filter(node = folder_id, content_id = 0).exists()

def scan_level(tree, user_id, node_id, level):
    for folder in Folder.objects.filter(user = user_id, node = node_id).order_by('code', 'name'):
        if not folder.content_id:
            tree.append(TreeNode(folder.id, node_id, folder.name, level, get_is_node(folder.id), folder.is_open, folder.icon, folder.color, folder.model_name))

            if folder.is_open:
                scan_level(tree, user_id, folder.id, level + 1)


def build_tree(user_id, node_id):
    tree = []
    scan_level(tree, user_id, node_id, 0)
    return tree


