from django.views.generic.edit import CreateView, UpdateView
from rusel.base.forms import GroupForm
from task.models import Group

class BaseListView(CreateView):

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        """
        if (config['view_as_tree']):
            self.template_name = 'base/tree.html'
        else:
            self.template_name = 'base/list.html'
        """
        self.template_name = 'base/list.html'


class BaseDetailView(UpdateView):

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.template_name = config['detail_template']

class BaseGroupView(UpdateView):
    model = Group
    template_name = 'base/group_detail.html'
    form_class = GroupForm

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
