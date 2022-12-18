from family.views.base import GenealogyListView
from family.models import (FamTreeUser, )

class CalendarListView(GenealogyListView):
    model = FamTreeUser
    template_name = 'family/calendar.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            return FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id)
        return []
