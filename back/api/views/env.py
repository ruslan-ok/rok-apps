import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils.translation import gettext_lazy as _
from core.context import Context, get_group_path
from task.models import Group

BG_IMAGES = [
    'beach',
    'desert',
    'fern',
    'field',
    'gradient',
    'lighthouse',
    'safari',
    'sea',
    'tv_tower'
]

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def env(request):
    context = Context()
    context.request = request
    app = request.query_params.get('app')
    group_id = request.query_params.get('group')
    if group_id:
        group_id = int(group_id)
    context.set_config(app)
    config = context.config
    config.set_view(request)

    data = {}
    data['title'] = config.title.capitalize()
    data['entity'] = config.group_entity
    data['add_item_placeholder'] = '{} {}'.format(_('add').capitalize(), config.item_name if config.item_name else config.get_cur_role_loc())
    data['icon'] = config.view_icon
    data['use_selector'] = config.use_selector
    data['use_important'] = config.use_important
    data['event_in_name'] = config.event_in_name

    group_path = []
    if group_id:
        group = Group.objects.filter(id=group_id).get()
        data['group_id'] = group_id
        if (not group.determinator) or (group.determinator == 'group'):
            group_path = get_group_path(group_id)
    data['group_path'] = group_path

    sorts = None
    grp = config.cur_view_group
    if grp:
        data.update({
            'theme_id': grp.theme,
            'dark_theme': grp.dark_theme(),
            'use_sub_groups': grp.use_sub_groups,
            'grp_view_id': grp.view_id,
            'grp_services_visible': grp.services_visible,
            'cur_view_group_id': grp.id,
            'determinator': grp.determinator,
        })
        if grp.items_sort:
            data['sort_id'] = grp.items_sort
            data['sort_reverse'] = grp.items_sort[0] == '-'
            if config.view_sorts:
                sorts = config.view_sorts
            else:
                sorts = config.app_sorts
            if sorts:
                for sort in sorts:
                    if (sort[0] == grp.items_sort.replace('-', '')):
                        data['sort_name'] = _(sort[1]).capitalize()
                        break
        if config.use_sub_groups:
            sub_groups = load_sub_groups(grp)
            data['sub_groups'] = sorted(sub_groups, key = lambda group: group['id'])
    data['sorts'] = [{'id': x[0], 'name': x[1].capitalize()} for x in sorts] if sorts else []
    data['related_roles'] = []
    data['possible_related'] = []
    themes = []
    for x in range(24):
        if (x < 14) or (x == 23):
            themes.append({'id': x+1, 'style': 'theme-' + str(x+1)})
        else:
            themes.append({'id': x+1, 'style': 'theme-' + str(x+1), 'img': BG_IMAGES[x-14]})
    data['themes'] = themes
    
    return Response(data)

def load_sub_groups(cur_group):
    ret = []
    if not cur_group:
        return ret
    if not cur_group.sub_groups:
        return ret
    sgs = json.loads(cur_group.sub_groups)
    for sg in sgs:
        ret.append({'id': sg['id'], 'name': sg['name'], 'is_open': sg['is_open']})
    return ret
