from django.db.models import Subquery
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.apart_select import ApartSelectForm
from apart.models import Apart, Meter, Price, Service, Bill

class BaseApartListView(BaseListView):

    def __init__(self, app_config, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'apart/list.html'

    def tune_dataset(self, data, view_mode):
        apart = Apart.objects.filter(user=self.request.user.id, active=True).get()
        if (view_mode == 'meter'):
            items = Meter.objects.filter(apart=apart.id)
            return data.filter(id__in=Subquery(items.values('task'))).order_by('-name')
        if (view_mode == 'service'):
            items = Service.objects.filter(apart=apart.id)
            return data.filter(id__in=Subquery(items.values('task')))
        if (view_mode == 'price'):
            items = Price.objects.filter(apart=apart.id)
            return data.filter(id__in=Subquery(items.values('task'))).order_by('-name')
        if (view_mode == 'bill'):
            items = Bill.objects.filter(apart=apart.id)
            return data.filter(id__in=Subquery(items.values('task'))).order_by('-name')
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ApartSelectForm(self.request.user)
        context.update({'apart_form': form})
        return context


class BaseApartDetailView(BaseDetailView):

    def __init__(self, app_config, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, view_mode):
        return data
