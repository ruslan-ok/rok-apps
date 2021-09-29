from rusel.base.views import BaseListView
from apart.forms.apart_select import ApartSelectForm
#from apart.models import Apart

class BaseApartListView(BaseListView):

    def __init__(self, app_config, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'apart/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ApartSelectForm(self.request.user)
        context.update({'apart_form': form})
        return context
