from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from core.context import Context, get_base_context
from task.const import APP_TODO

class TodoViewSet(ViewSet):

    def list(self, request):
        context = Context()
        context.request = request
        context.set_config(APP_TODO)
        context.config.set_view(request)
        context_data = get_base_context(
            request, 
            APP_TODO, 
            context.config.get_cur_role(), 
            context.config.cur_view_group, 
            detail=False, 
            title="", 
            icon=None
        )
        groups = [
            {
                'id': x.id,
                'node_id': x.node.id if x.node else None,
                'name': x.name,
                'is_leaf': x.is_leaf(),
                'level': x.level(),
                'act_items_qty': x.act_items_qty,
            } for x in context_data['groups']]
        
        fixes = context.get_fixes(context.config.views, search_qty=None)

        data = {
            'sideBarData': {
                'fixes': fixes,
                'use_groups': True,
                'groups': groups,
                'dirs': [],
                'navs': [],
                'list_href': False,
                'cur_view': '',
                'app': context.config.app,
                'role': '',
                'entity': context.config.group_entity,
                'current': context.config.cur_view_group.id,
                'create_group_hint': '',
            }
        }
        return Response(data)
