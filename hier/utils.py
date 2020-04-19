from enum import Enum
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from .models import File
from .tree import build_tree

"""
class StorageTypes(Enum):
    NONE = 0
    TRASH = 1
    FUEL = 2
    TRIP = 3
    APART = 4
    ENTRY = 5
    WORK = 6

STORAGE_TYPES = (
    (StorageTypes.NONE,    '------'),
    (StorageTypes.TRASH, _('trash').capitalize()),
    (StorageTypes.FUEL,  _('fueling').capitalize()),
    (StorageTypes.TRIP,  _('trips').capitalize()),
    (StorageTypes.APART, _('apartment').capitalize()),
    (StorageTypes.ENTRY, _('passwords').capitalize()),
    (StorageTypes.WORK,  _('work').capitalize())
)
"""

i_storage_type = {
    'none':  0,
    'trash': 1,
    'fuel':  2,
    'trip':  3,
    'apart': 4,
    'entry': 5,
    'work':  6 }

s_storage_type = {
    'none':  '------',
    'trash': _('trash').capitalize(),
    'fuel':  _('fueling').capitalize(),
    'trip':  _('trips').capitalize(),
    'apart': _('apartment').capitalize(),
    'entry': _('passwords').capitalize(),
    'work':  _('work').capitalize() }

STORAGE_TYPES = (
    (i_storage_type['none'],  s_storage_type['none']),
    (i_storage_type['trash'], s_storage_type['trash']),
    (i_storage_type['fuel'],  s_storage_type['fuel']),
    (i_storage_type['trip'],  s_storage_type['trip']),
    (i_storage_type['apart'], s_storage_type['apart']),
    (i_storage_type['entry'], s_storage_type['entry']),
    (i_storage_type['work'],  s_storage_type['work']))


def get_trash(user):
    trash_id = i_storage_type['trash']
    if File.objects.filter(user = user.id, node = 0, storage = trash_id).exists():
        return File.objects.filter(user = user.id, node = 0, storage = trash_id)[0]
    return File.objects.create(user = user, node = 0, storage = trash_id, name = _('trash').capitalize())

def rmtree(user, file_id):
    if not File.objects.filter(user = user.id, id = file_id).exists():
        return
    node = File.objects.filter(id = file_id).get()
    for file in File.objects.filter(user = user.id, node = node.id):
        file.node = get_trash(user).id
        file.save()


def check_health(user_id, node_id):
    level_qty = 0
    for file in File.objects.filter(user = user_id, node = node_id):
        check_health(user_id, file.id)
        level_qty = level_qty + 1
    if (node_id != 0):
        node = File.objects.filter(user = user_id, id = node_id).get()
        node.qty = level_qty
        node.save()

#----------------------------------
# Контекст для любой страницы
#----------------------------------
def get_base_context(request, node_id, pk, title, app = ''):
    context = {}
    context['site_header'] = get_current_site(request).name
    context['pk'] = pk
    context['title'] = title

    if (node_id == 0) and (app != ''):
        if File.objects.filter(user = request.user.id, app = app).exists():
            node_id = File.objects.filter(user = request.user.id, app = app)[0].id
    context['node_id'] = node_id

    if request.user.is_authenticated:
        tree = build_tree(request.user.id, 0)
    else:
        tree = []
    context['tree'] = tree

    chain = []
    while (node_id != 0):
        if File.objects.filter(user = request.user.id, id = node_id).exists():
            node = File.objects.filter(user = request.user.id, id = node_id)[0]
            chain.append(node)
            node_id = node.node
        else:
            break 
    context['chain'] = chain

    return context





