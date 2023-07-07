import os
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from task.const import *
from core.views import Context

from task.models import Group #Task, detect_group

app = APP_CRAM
role = ROLE_CRAM

class CramContext(Context):

    def get_fixes(self, views, search_qty):
        fixes = []
        nav_group = None
        if Group.objects.filter(user=self.request.user.id, app=app, role=role).exists():
            nav_group = Group.objects.filter(user=self.request.user.id, app=app, role=role)[0]
        for key, value in views.items():
            if 'hide_on_host' in value:
                if value['hide_on_host'] == os.environ.get('DJANGO_HOST'):
                    continue
            determinator = 'view'
            view_id = self.config.main_view
            match key:
                case 'index': url = reverse('cram:list') #+ '?group=' + str(nav_group.id)
                # case 'languages': url = reverse('cram:lang-list')
                # case 'phrases': url = reverse('cram:phrase-list', args=(nav_group.id,))
                # case 'training': url = reverse('cram:training', args=(nav_group.id, 0, 'en'))
                case _: url = reverse('cram:list')
            active = (self.config.cur_view_group.determinator == determinator) and (self.config.cur_view_group.view_id == view_id)
            qty = None
            if not self.config.global_hide_qty:
                hide_qty = False
                if ('hide_qty' in value):
                    hide_qty = value['hide_qty']
                if hide_qty:
                    if active and hasattr(self, 'object_list'):
                        qty = len(self.object_list)
                else:
                    if (view_id == self.config.group_entity):
                        _nav_item = None
                    else:
                        _nav_item = nav_item
                    fix_group = detect_group(self.request.user, self.config.app, determinator, view_id, value['title'].capitalize())
                    qty = self.get_view_qty(fix_group, _nav_item)
            fix = {
                'determinator': determinator,
                'id': view_id, 
                'url': url, 
                'icon': value['icon'], 
                'title': _(value['title']),
                'qty': qty,
                'active': active,
                'search_qty': search_qty,
            }
            fixes.append(fix)
        return fixes

    # def get_active_group(self, cur_group: Group|None) -> Group|None:
    #     if cur_group:
    #         app = cur_group.app
    #         determinator = cur_group.determinator
    #         view_id = cur_group.view_id
    #     if Group.objects.filter(user=self.request.user.id, app=app, role=ROLE_CRAM_PARAM).exists():
    #         param = Group.objects.filter(user=self.request.user.id, app=app, role=ROLE_CRAM_PARAM).get()
    #         return param
    #     return None

    # def set_active_group(self, group: Group):
    #     if Group.objects.filter(user=self.request.user.id, app=app, role=ROLE_CRAM_PARAM).exists():
    #         param = Group.objects.filter(user=self.request.user.id, app=app, role=ROLE_CRAM_PARAM).get()
    #         param.node = group
    #         param.save()
    #     else:
    #         param = Group.objects.create(user=self.request.user, app=app, role=ROLE_CRAM_PARAM, node=group)
